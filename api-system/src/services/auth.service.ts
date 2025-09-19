import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import { DatabaseService } from '../services/database.service';
import { EmailService } from '../services/email.service';
import { CacheService } from '../services/cache.service';
import { logger } from '../utils/logger';

export interface User {
  id: string;
  email: string;
  username: string;
  passwordHash: string;
  firstName?: string;
  lastName?: string;
  phone?: string;
  avatarUrl?: string;
  bio?: string;
  isActive: boolean;
  isVerified: boolean;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Session {
  id: string;
  userId: string;
  refreshToken: string;
  accessToken: string;
  deviceInfo: any;
  ipAddress: string;
  userAgent: string;
  expiresAt: Date;
  isActive: boolean;
  createdAt: Date;
  lastUsed: Date;
}

export class AuthService {
  private db: DatabaseService;
  private emailService: EmailService;
  private cacheService: CacheService;
  private saltRounds: number = 12;

  constructor() {
    this.db = new DatabaseService();
    this.emailService = new EmailService();
    this.cacheService = new CacheService();
  }

  /**
   * Register a new user
   */
  public async register(userData: {
    email: string;
    username: string;
    password: string;
    firstName?: string;
    lastName?: string;
    phone?: string;
  }): Promise<{
    user: Omit<User, 'passwordHash'>;
    accessToken: string;
    refreshToken: string;
  }> {
    // Check if user already exists
    const existingUser = await this.db.query(
      'SELECT id, email, username FROM users WHERE email = $1 OR username = $2',
      [userData.email, userData.username]
    );

    if (existingUser.rows.length > 0) {
      throw new Error('User with this email or username already exists');
    }

    // Hash password
    const passwordHash = await bcrypt.hash(userData.password, this.saltRounds);

    // Create user
    const userResult = await this.db.query(
      `INSERT INTO users (id, email, username, password_hash, first_name, last_name, phone)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING id, email, username, first_name, last_name, phone, avatar_url, bio, is_active, is_verified, email_verified, created_at, updated_at`,
      [
        uuidv4(),
        userData.email,
        userData.username,
        passwordHash,
        userData.firstName,
        userData.lastName,
        userData.phone
      ]
    );

    const user = userResult.rows[0];

    // Assign default role
    await this.db.query(
      `INSERT INTO user_roles (id, user_id, role_id, assigned_by)
       VALUES ($1, $2, (SELECT id FROM roles WHERE name = 'user'), $3)`,
      [uuidv4(), user.id, user.id]
    );

    // Generate JWT tokens
    const { accessToken, refreshToken } = await this.generateTokens(user.id);

    // Create session
    await this.createSession(user.id, accessToken, refreshToken, {
      userAgent: 'registration',
      ipAddress: 'unknown'
    });

    // Send verification email
    await this.sendVerificationEmail(user.id, user.email);

    // Log registration
    logger.info('User registered', {
      userId: user.id,
      email: user.email,
      username: user.username
    });

    return {
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        firstName: user.first_name,
        lastName: user.last_name,
        phone: user.phone,
        avatarUrl: user.avatar_url,
        bio: user.bio,
        isActive: user.is_active,
        isVerified: user.is_verified,
        emailVerified: user.email_verified,
        createdAt: user.created_at,
        updatedAt: user.updated_at
      },
      accessToken,
      refreshToken
    };
  }

  /**
   * Login user
   */
  public async login(credentials: {
    email: string;
    password: string;
    rememberMe?: boolean;
    userAgent?: string;
    ipAddress?: string;
  }): Promise<{
    user: Omit<User, 'passwordHash'>;
    accessToken: string;
    refreshToken: string;
  }> {
    // Find user
    const userResult = await this.db.query(
      'SELECT id, email, username, password_hash, first_name, last_name, phone, avatar_url, bio, is_active, is_verified, email_verified, created_at, updated_at FROM users WHERE email = $1',
      [credentials.email]
    );

    if (userResult.rows.length === 0) {
      throw new Error('Invalid credentials');
    }

    const user = userResult.rows[0];

    // Check if user is active
    if (!user.is_active) {
      throw new Error('Account is deactivated');
    }

    // Verify password
    const isPasswordValid = await bcrypt.compare(credentials.password, user.password_hash);
    if (!isPasswordValid) {
      throw new Error('Invalid credentials');
    }

    // Generate JWT tokens
    const { accessToken, refreshToken } = await this.generateTokens(
      user.id,
      credentials.rememberMe ? '30d' : '1h'
    );

    // Create session
    await this.createSession(user.id, accessToken, refreshToken, {
      userAgent: credentials.userAgent,
      ipAddress: credentials.ipAddress
    });

    // Update last login
    await this.db.query(
      'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1',
      [user.id]
    );

    // Log login
    logger.info('User logged in', {
      userId: user.id,
      email: user.email,
      ipAddress: credentials.ipAddress
    });

    return {
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        firstName: user.first_name,
        lastName: user.last_name,
        phone: user.phone,
        avatarUrl: user.avatar_url,
        bio: user.bio,
        isActive: user.is_active,
        isVerified: user.is_verified,
        emailVerified: user.email_verified,
        createdAt: user.created_at,
        updatedAt: user.updated_at
      },
      accessToken,
      refreshToken
    };
  }

  /**
   * Refresh access token
   */
  public async refreshToken(refreshToken: string): Promise<{
    accessToken: string;
    refreshToken: string;
  }> {
    try {
      // Verify refresh token
      const decoded = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET!) as {
        userId: string;
        sessionId: string;
      };

      // Check if session exists and is active
      const sessionResult = await this.db.query(
        'SELECT id, user_id, is_active, expires_at FROM user_sessions WHERE refresh_token = $1',
        [refreshToken]
      );

      if (sessionResult.rows.length === 0) {
        throw new Error('Invalid refresh token');
      }

      const session = sessionResult.rows[0];

      if (!session.is_active || new Date() > session.expires_at) {
        // Deactivate expired session
        await this.db.query(
          'UPDATE user_sessions SET is_active = false WHERE id = $1',
          [session.id]
        );
        throw new Error('Session expired');
      }

      // Generate new tokens
      const { accessToken, refreshToken: newRefreshToken } = await this.generateTokens(
        session.user_id
      );

      // Update session with new tokens
      await this.db.query(
        'UPDATE user_sessions SET access_token = $1, refresh_token = $2, last_used = CURRENT_TIMESTAMP WHERE id = $3',
        [accessToken, newRefreshToken, session.id]
      );

      return {
        accessToken,
        refreshToken: newRefreshToken
      };
    } catch (error) {
      if (error instanceof jwt.JsonWebTokenError) {
        throw new Error('Invalid refresh token');
      }
      throw error;
    }
  }

  /**
   * Logout user
   */
  public async logout(accessToken: string): Promise<void> {
    try {
      const decoded = jwt.verify(accessToken, process.env.JWT_SECRET!) as {
        userId: string;
        sessionId: string;
      };

      // Deactivate session
      await this.db.query(
        'UPDATE user_sessions SET is_active = false WHERE id = $1',
        [decoded.sessionId]
      );

      // Clear user from cache
      await this.cacheService.delete(`user:${decoded.userId}`);

      logger.info('User logged out', {
        userId: decoded.userId,
        sessionId: decoded.sessionId
      });
    } catch (error) {
      // Even if token is invalid, attempt to logout
      logger.warn('Logout attempt with invalid token');
    }
  }

  /**
   * Send password reset email
   */
  public async forgotPassword(email: string): Promise<void> {
    const userResult = await this.db.query(
      'SELECT id, email FROM users WHERE email = $1 AND is_active = true',
      [email]
    );

    if (userResult.rows.length === 0) {
      // Don't reveal if user exists
      return;
    }

    const user = userResult.rows[0];

    // Generate reset token
    const resetToken = jwt.sign(
      { userId: user.id, type: 'password_reset' },
      process.env.JWT_SECRET!,
      { expiresIn: '1h' }
    );

    // Store reset token in cache
    await this.cacheService.set(
      `password_reset:${user.id}`,
      resetToken,
      3600 // 1 hour
    );

    // Send reset email
    await this.emailService.sendPasswordResetEmail(user.email, resetToken);

    logger.info('Password reset requested', {
      userId: user.id,
      email: user.email
    });
  }

  /**
   * Reset password
   */
  public async resetPassword(token: string, newPassword: string): Promise<void> {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
        userId: string;
        type: 'password_reset';
      };

      if (decoded.type !== 'password_reset') {
        throw new Error('Invalid token type');
      }

      // Verify token from cache
      const cachedToken = await this.cacheService.get(`password_reset:${decoded.userId}`);
      if (cachedToken !== token) {
        throw new Error('Invalid or expired token');
      }

      // Hash new password
      const passwordHash = await bcrypt.hash(newPassword, this.saltRounds);

      // Update password
      await this.db.query(
        'UPDATE users SET password_hash = $1 WHERE id = $2',
        [passwordHash, decoded.userId]
      );

      // Invalidate all user sessions
      await this.db.query(
        'UPDATE user_sessions SET is_active = false WHERE user_id = $1',
        [decoded.userId]
      );

      // Clear cache
      await this.cacheService.delete(`password_reset:${decoded.userId}`);
      await this.cacheService.delete(`user:${decoded.userId}`);

      logger.info('Password reset successful', {
        userId: decoded.userId
      });
    } catch (error) {
      if (error instanceof jwt.JsonWebTokenError) {
        throw new Error('Invalid or expired token');
      }
      throw error;
    }
  }

  /**
   * Verify email
   */
  public async verifyEmail(token: string): Promise<void> {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as {
        userId: string;
        type: 'email_verification';
      };

      if (decoded.type !== 'email_verification') {
        throw new Error('Invalid token type');
      }

      // Update user email verification status
      await this.db.query(
        'UPDATE users SET email_verified = true WHERE id = $1',
        [decoded.userId]
      );

      logger.info('Email verified', {
        userId: decoded.userId
      });
    } catch (error) {
      if (error instanceof jwt.JsonWebTokenError) {
        throw new Error('Invalid or expired token');
      }
      throw error;
    }
  }

  /**
   * Generate JWT tokens
   */
  private async generateTokens(
    userId: string,
    expiresIn: string = '1h'
  ): Promise<{ accessToken: string; refreshToken: string }> {
    const sessionId = uuidv4();

    const accessToken = jwt.sign(
      { userId, type: 'access', sessionId },
      process.env.JWT_SECRET!,
      { expiresIn }
    );

    const refreshToken = jwt.sign(
      { userId, type: 'refresh', sessionId },
      process.env.JWT_REFRESH_SECRET!,
      { expiresIn: '30d' }
    );

    return { accessToken, refreshToken };
  }

  /**
   * Create user session
   */
  private async createSession(
    userId: string,
    accessToken: string,
    refreshToken: string,
    deviceInfo: { userAgent?: string; ipAddress?: string }
  ): Promise<void> {
    const sessionId = uuidv4();
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 30); // 30 days

    await this.db.query(
      `INSERT INTO user_sessions (id, user_id, refresh_token, access_token, device_info, ip_address, user_agent, expires_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)`,
      [
        sessionId,
        userId,
        refreshToken,
        accessToken,
        deviceInfo,
        deviceInfo.ipAddress,
        deviceInfo.userAgent,
        expiresAt
      ]
    );
  }

  /**
   * Send verification email
   */
  private async sendVerificationEmail(userId: string, email: string): Promise<void> {
    const verificationToken = jwt.sign(
      { userId, type: 'email_verification' },
      process.env.JWT_SECRET!,
      { expiresIn: '24h' }
    );

    await this.emailService.sendVerificationEmail(email, verificationToken);
  }

  /**
   * Clean up expired sessions
   */
  public async cleanupExpiredSessions(): Promise<void> {
    await this.db.query(
      'UPDATE user_sessions SET is_active = false WHERE expires_at < CURRENT_TIMESTAMP'
    );

    logger.info('Expired sessions cleaned up');
  }
}