import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
Config.setPixelFormat('yuv420p');
Config.setCodec('h264');

// Quality settings
Config.setJpegQuality(80);
Config.setCrf(23);

// Performance settings
Config.setConcurrency(4);

// Audio settings
Config.setAudioCodec('aac');

export default Config;