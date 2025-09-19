import { Logger } from '../../src/utils/Logger';

describe('Logger', () => {
  let logger: Logger;
  let consoleSpy: jest.SpyInstance;

  beforeEach(() => {
    logger = new Logger('TestService');
    consoleSpy = jest.spyOn(console, 'log').mockImplementation();
  });

  afterEach(() => {
    consoleSpy.mockRestore();
  });

  describe('constructor', () => {
    it('should create logger with service name', () => {
      const logger = new Logger('MyService');
      expect(logger).toBeDefined();
    });
  });

  describe('info', () => {
    it('should log info message', () => {
      logger.info('Test message');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('should log info message with metadata', () => {
      const metadata = { userId: '123', action: 'test' };
      logger.info('Test message', metadata);

      expect(consoleSpy).toHaveBeenCalled();
    });
  });

  describe('error', () => {
    it('should log error message', () => {
      logger.error('Test error');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('should log error message with error object', () => {
      const error = new Error('Test error');
      logger.error('Test error', error);

      expect(consoleSpy).toHaveBeenCalled();
    });
  });

  describe('warn', () => {
    it('should log warning message', () => {
      logger.warn('Test warning');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('should log warning message with metadata', () => {
      const metadata = { warning: 'true' };
      logger.warn('Test warning', metadata);

      expect(consoleSpy).toHaveBeenCalled();
    });
  });

  describe('debug', () => {
    it('should log debug message', () => {
      logger.debug('Test debug');

      expect(consoleSpy).toHaveBeenCalled();
    });

    it('should log debug message with metadata', () => {
      const metadata = { debug: 'true' };
      logger.debug('Test debug', metadata);

      expect(consoleSpy).toHaveBeenCalled();
    });
  });
});