import {Composition} from 'remotion';
import {ThariqReply} from './ThariqReply';

export const RemotionRoot: React.FC = () => {
	return (
		<>
			<Composition
				id="ThariqReply"
				component={ThariqReply}
				durationInFrames={900} // 30 seconds at 30fps
				fps={30}
				width={1920}
				height={1080}
				defaultProps={{}}
			/>
		</>
	);
};