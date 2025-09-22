import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

interface VideoProps {
	clip: {
		id: string;
		startFrame: number;
		endFrame: number;
		background: string;
		theme: string;
	};
	frame: number;
	globalFrame: number;
}

export const Video: React.FC<VideoProps> = ({clip, frame, globalFrame}) => {
	const {fps} = useVideoConfig();

	// Animation values based on clip frame
	const fadeIn = interpolate(frame, [0, 30], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const scaleAnimation = interpolate(frame, [0, 60], [0.8, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const slideUp = interpolate(frame, [0, 45], [50, 0], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	// Content based on clip theme
	const getClipContent = () => {
		switch (clip.theme) {
			case 'intro':
				return {
					title: 'Welcome to Our Journey',
					subtitle: 'Discover Amazing Stories',
					description: 'Join us as we explore incredible narratives and experiences',
					color: '#ff6b6b',
					accent: '#4ecdc4'
				};
			case 'main':
				return {
					title: 'The Main Story',
					subtitle: 'Deep Dive Experience',
					description: 'Immerse yourself in rich content and compelling visuals',
					color: '#45b7d1',
					accent: '#96ceb4'
				};
			case 'outro':
				return {
					title: 'Thank You',
					subtitle: 'Until Next Time',
					description: 'We hope you enjoyed this journey with us',
					color: '#9b59b6',
					accent: '#f39c12'
				};
			default:
				return {
					title: 'Video Content',
					subtitle: 'Engaging Experience',
					description: 'Professional video presentation',
					color: '#3498db',
					accent: '#e74c3c'
				};
		}
	};

	const content = getClipContent();

	// Particle animation
	const particleOffset = (globalFrame * 0.5) % 360;

	// Text animations with staggered timing
	const titleDelay = 15;
	const subtitleDelay = 30;
	const descDelay = 45;

	const titleOpacity = interpolate(frame, [titleDelay, titleDelay + 20], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const subtitleOpacity = interpolate(frame, [subtitleDelay, subtitleDelay + 20], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	const descOpacity = interpolate(frame, [descDelay, descDelay + 20], [0, 1], {
		extrapolateLeft: 'clamp',
		extrapolateRight: 'clamp',
	});

	return (
		<div
			style={{
				width: '100%',
				height: '100%',
				position: 'relative',
				display: 'flex',
				flexDirection: 'column',
				justifyContent: 'center',
				alignItems: 'center',
				overflow: 'hidden',
			}}
		>
			{/* Background Audio - removed for rendering */}

			{/* Animated Background Particles */}
			{Array.from({length: 12}).map((_, i) => (
				<div
					key={i}
					style={{
						position: 'absolute',
						width: 4 + (i % 3) * 2,
						height: 4 + (i % 3) * 2,
						borderRadius: '50%',
						backgroundColor: i % 2 === 0 ? content.color : content.accent,
						left: `${10 + (i * 8)}%`,
						top: `${20 + Math.sin((particleOffset + i * 30) * Math.PI / 180) * 30}%`,
						opacity: 0.6,
						transform: `scale(${scaleAnimation})`,
					}}
				/>
			))}

			{/* Main Content Container */}
			<div
				style={{
					textAlign: 'center',
					transform: `translateY(${slideUp}px) scale(${scaleAnimation})`,
					opacity: fadeIn,
					maxWidth: '80%',
					zIndex: 5,
				}}
			>
				{/* Main Title */}
				<h1
					style={{
						fontSize: 72,
						fontWeight: 'bold',
						color: content.color,
						margin: 0,
						marginBottom: 20,
						fontFamily: 'Arial, sans-serif',
						textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
						opacity: titleOpacity,
						transform: `translateY(${interpolate(frame, [titleDelay, titleDelay + 20], [20, 0])})`,
					}}
				>
					{content.title}
				</h1>

				{/* Subtitle */}
				<h2
					style={{
						fontSize: 36,
						color: content.accent,
						margin: 0,
						marginBottom: 30,
						fontFamily: 'Arial, sans-serif',
						fontWeight: 300,
						opacity: subtitleOpacity,
						transform: `translateY(${interpolate(frame, [subtitleDelay, subtitleDelay + 20], [20, 0])})`,
					}}
				>
					{content.subtitle}
				</h2>

				{/* Description */}
				<p
					style={{
						fontSize: 24,
						color: 'white',
						lineHeight: 1.6,
						margin: 0,
						fontFamily: 'Arial, sans-serif',
						opacity: descOpacity,
						transform: `translateY(${interpolate(frame, [descDelay, descDelay + 20], [20, 0])})`,
					}}
				>
					{content.description}
				</p>
			</div>

			{/* Progress Bar */}
			<div
				style={{
					position: 'absolute',
					bottom: 40,
					left: '10%',
					right: '10%',
					height: 4,
					backgroundColor: 'rgba(255, 255, 255, 0.2)',
					borderRadius: 2,
					overflow: 'hidden',
					zIndex: 10,
				}}
			>
				<div
					style={{
						height: '100%',
						backgroundColor: content.color,
						width: `${(frame / 300) * 100}%`,
						borderRadius: 2,
						transition: 'width 0.1s ease',
					}}
				/>
			</div>

			{/* Subtitle Overlay System */}
			<SubtitleOverlay frame={frame} clip={clip} />
		</div>
	);
};

// Subtitle Overlay Component
const SubtitleOverlay: React.FC<{frame: number, clip: any}> = ({frame, clip}) => {
	const getSubtitleText = (frame: number, theme: string) => {
		const timeInSeconds = Math.floor(frame / 30);

		const subtitles = {
			intro: [
				{start: 0, end: 3, text: "Welcome to our amazing journey"},
				{start: 3, end: 6, text: "Prepare for an incredible experience"},
				{start: 6, end: 10, text: "Let's begin this adventure together"}
			],
			main: [
				{start: 0, end: 4, text: "This is where the magic happens"},
				{start: 4, end: 8, text: "Deep dive into compelling content"},
				{start: 8, end: 10, text: "Experience rich storytelling"}
			],
			outro: [
				{start: 0, end: 3, text: "Thank you for joining us"},
				{start: 3, end: 6, text: "We hope you enjoyed the journey"},
				{start: 6, end: 10, text: "See you next time!"}
			]
		};

		const currentSubtitles = subtitles[theme as keyof typeof subtitles] || [];
		const currentSubtitle = currentSubtitles.find(
			sub => timeInSeconds >= sub.start && timeInSeconds < sub.end
		);

		return currentSubtitle?.text || '';
	};

	const subtitleText = getSubtitleText(frame, clip.theme);

	if (!subtitleText) return null;

	return (
		<div
			style={{
				position: 'absolute',
				bottom: 100,
				left: '50%',
				transform: 'translateX(-50%)',
				backgroundColor: 'rgba(0, 0, 0, 0.8)',
				padding: '12px 24px',
				borderRadius: 25,
				color: 'white',
				fontSize: 20,
				fontFamily: 'Arial, sans-serif',
				textAlign: 'center',
				maxWidth: '80%',
				zIndex: 15,
			}}
		>
			{subtitleText}
		</div>
	);
};