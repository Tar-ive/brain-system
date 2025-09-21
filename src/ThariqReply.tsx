import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';
import { TransitionSeries, linearTiming, springTiming } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { slide } from '@remotion/transitions/slide';
import { DynamicSubtitles } from './Subtitles';

// Clip 1: Intro (0-300 frames / 10 seconds)
const IntroClip: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Animated code compilation effect
  const codeProgress = interpolate(frame, [0, 150], [0, 100], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const titleOpacity = spring({
    fps,
    frame,
    config: { damping: 200 },
  });

  const codeScale = spring({
    fps,
    frame: frame - 30,
    config: { damping: 100 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#0f172a' }}>
      {/* Animated title */}
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          opacity: titleOpacity,
        }}
      >
        <div
          style={{
            fontSize: 72,
            fontFamily: 'SF Pro Display, Arial, sans-serif',
            fontWeight: 'bold',
            color: '#ffffff',
            textAlign: 'center',
            textShadow: '0 4px 12px rgba(0,0,0,0.5)',
          }}
        >
          Hey Thariq! 👋
        </div>
      </AbsoluteFill>

      {/* Code compilation animation */}
      <Sequence from={30} durationInFrames={270}>
        <AbsoluteFill
          style={{
            justifyContent: 'center',
            alignItems: 'center',
            transform: `scale(${codeScale})`,
          }}
        >
          <div
            style={{
              width: '80%',
              maxWidth: 800,
              backgroundColor: '#1e293b',
              borderRadius: 12,
              padding: 30,
              boxShadow: '0 10px 40px rgba(0,0,0,0.3)',
            }}
          >
            <div
              style={{
                fontFamily: 'Monaco, monospace',
                fontSize: 18,
                color: '#64748b',
                marginBottom: 20,
              }}
            >
              // Claude Code in action...
            </div>
            <div
              style={{
                background: `linear-gradient(90deg, #3b82f6 ${codeProgress}%, #1e293b ${codeProgress}%)`,
                height: 8,
                borderRadius: 4,
                marginBottom: 20,
              }}
            />
            <pre
              style={{
                fontFamily: 'Monaco, monospace',
                fontSize: 16,
                color: '#e2e8f0',
                margin: 0,
                whiteSpace: 'pre-wrap',
              }}
            >
              {`const video = await remotion.render({
  composition: 'ThariqReply',
  codec: 'h264',
  fps: 30
});`}
            </pre>
            <div
              style={{
                marginTop: 20,
                fontSize: 14,
                color: '#94a3b8',
              }}
            >
              Compiling... {Math.round(codeProgress)}%
            </div>
          </div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

// Clip 2: Demo (300-600 frames / 10 seconds)
const DemoClip: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const textReveal = interpolate(frame, [0, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const highlightScale = spring({
    fps,
    frame: frame - 90,
    config: { damping: 150 },
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#1a1b3a' }}>
      {/* Reply text overlay with effects */}
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          padding: 50,
        }}
      >
        <div
          style={{
            backgroundColor: 'rgba(30, 41, 59, 0.95)',
            borderRadius: 20,
            padding: 40,
            maxWidth: '90%',
            boxShadow: '0 20px 60px rgba(0,0,0,0.4)',
            border: '2px solid #3b82f6',
            opacity: textReveal,
          }}
        >
          <div
            style={{
              fontSize: 28,
              fontFamily: 'Inter, Arial, sans-serif',
              color: '#f1f5f9',
              lineHeight: 1.6,
              marginBottom: 30,
            }}
          >
            "Loved your Claude Code video editing tips! 🎬"
          </div>

          <div
            style={{
              fontSize: 24,
              fontFamily: 'Inter, Arial, sans-serif',
              color: '#cbd5e1',
              lineHeight: 1.6,
            }}
          >
            Here's my take: Claude Code + Remotion =
            <span
              style={{
                color: '#3b82f6',
                fontWeight: 'bold',
                display: 'inline-block',
                transform: `scale(${highlightScale})`,
                marginLeft: 10,
              }}
            >
              Pure Magic ✨
            </span>
          </div>

          <div
            style={{
              marginTop: 30,
              fontSize: 18,
              color: '#94a3b8',
              fontStyle: 'italic',
            }}
          >
            // Generating videos with AI assistance
          </div>
        </div>
      </AbsoluteFill>

      {/* Animated background particles */}
      <Sequence from={120} durationInFrames={180}>
        <AbsoluteFill>
          {[...Array(5)].map((_, i) => {
            const particleY = interpolate(
              frame - 120,
              [0, 180],
              [1080, -100],
              {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              }
            );

            return (
              <div
                key={i}
                style={{
                  position: 'absolute',
                  left: `${20 + i * 20}%`,
                  top: particleY + i * 50,
                  width: 8,
                  height: 8,
                  backgroundColor: '#3b82f6',
                  borderRadius: '50%',
                  opacity: 0.6,
                }}
              />
            );
          })}
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

// Clip 3: Closing (600-900 frames / 10 seconds)
const ClosingClip: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const thanksScale = spring({
    fps,
    frame,
    config: { damping: 100 },
  });

  const fadeOut = interpolate(frame, [200, 300], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: '#0f172a' }}>
      {/* Thank you message */}
      <AbsoluteFill
        style={{
          justifyContent: 'center',
          alignItems: 'center',
          opacity: fadeOut,
        }}
      >
        <div
          style={{
            transform: `scale(${thanksScale})`,
            textAlign: 'center',
          }}
        >
          <div
            style={{
              fontSize: 64,
              fontFamily: 'SF Pro Display, Arial, sans-serif',
              fontWeight: 'bold',
              color: '#ffffff',
              marginBottom: 30,
              textShadow: '0 4px 12px rgba(0,0,0,0.5)',
            }}
          >
            Thanks for the inspo! 🚀
          </div>

          <div
            style={{
              fontSize: 32,
              fontFamily: 'Inter, Arial, sans-serif',
              color: '#94a3b8',
              marginTop: 20,
            }}
          >
            Keep creating amazing content!
          </div>

          <div
            style={{
              marginTop: 40,
              fontSize: 20,
              color: '#64748b',
              fontFamily: 'Monaco, monospace',
            }}
          >
            // Made with Claude Code + Remotion
          </div>
        </div>
      </AbsoluteFill>

      {/* Animated logo/signature */}
      <Sequence from={150} durationInFrames={150}>
        <AbsoluteFill
          style={{
            bottom: 50,
            justifyContent: 'center',
            alignItems: 'flex-end',
          }}
        >
          <div
            style={{
              padding: '10px 20px',
              backgroundColor: '#3b82f6',
              borderRadius: 8,
              fontSize: 16,
              color: '#ffffff',
              fontWeight: 'bold',
            }}
          >
            #ClaudeCode #Remotion
          </div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};

// Main composition
export const ThariqReply: React.FC = () => {
  return (
    <AbsoluteFill>
      <TransitionSeries>
        <TransitionSeries.Sequence durationInFrames={300}>
          <IntroClip />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          timing={springTiming({ config: { damping: 200 }, durationInFrames: 30 })}
          presentation={slide({ direction: 'from-right' })}
        />

        <TransitionSeries.Sequence durationInFrames={300}>
          <DemoClip />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition
          timing={linearTiming({ durationInFrames: 30 })}
          presentation={fade()}
        />

        <TransitionSeries.Sequence durationInFrames={300}>
          <ClosingClip />
        </TransitionSeries.Sequence>
      </TransitionSeries>

      {/* Subtitles overlay */}
      <DynamicSubtitles />

      {/* Audio placeholder - replace with actual voiceover */}
      {/* <Audio src={staticFile('voiceover.mp3')} volume={0.8} /> */}
    </AbsoluteFill>
  );
};