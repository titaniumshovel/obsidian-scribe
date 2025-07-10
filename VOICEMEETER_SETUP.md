# VoiceMeeter Setup for Obsidian Audio Recording

## Overview

This guide explains how to configure VoiceMeeter Banana on Windows to record both your microphone and system audio (e.g., Teams meetings) as a single mixed audio stream for use with Obsidian's Whisper plugin and subsequent processing by Obsidian Scribe.

## Why VoiceMeeter?

The Obsidian Whisper community plugin can only record from a single audio input device. To capture both your voice and other participants in a Teams meeting, we need to:
1. Mix multiple audio sources into one stream
2. Present this mixed stream as a virtual microphone to Obsidian

VoiceMeeter Banana provides this capability through virtual audio routing.

## Prerequisites

1. **Download VoiceMeeter Banana** (free)
   - Download from: https://vb-audio.com/Voicemeeter/banana.htm
   - Install and restart your computer

2. **Install VB-Cable** (free, optional but recommended)
   - Download from: https://vb-audio.com/Cable/
   - Provides additional virtual audio cable for routing

## Configuration Steps

### Step 1: VoiceMeeter Setup

1. **Launch VoiceMeeter Banana**

2. **Configure Hardware Inputs**
   - **Hardware Input 1**: Click and select your microphone
   - **Hardware Input 2**: Set to "VB-Audio Virtual Cable" (if installed)
   - This allows Teams audio to be routed through VB-Cable

3. **Configure Virtual Inputs**
   - The Virtual Input (VAIO) can capture system sounds
   - This is useful if you want to include other audio sources

### Step 2: Audio Routing

1. **Route Microphone to B1**
   - On Hardware Input 1 strip, click the "B1" button to enable
   - This sends your microphone audio to the B1 virtual output

2. **Route Teams Audio to B1**
   - On Hardware Input 2 strip, click the "B1" button to enable
   - This sends Teams audio (via VB-Cable) to the B1 virtual output

3. **Optional: Route System Sounds**
   - On the Virtual Input strip, click "B1" if you want system sounds included

### Step 3: Windows Audio Configuration

1. **Set Default Recording Device**
   - Open Windows Sound Settings
   - Go to "Recording" tab
   - Set "VoiceMeeter Output (VB-Audio VoiceMeeter VAIO)" as default
   - This is the B1 output that contains your mixed audio

2. **Configure Teams Audio Output**
   - In Teams settings, set Speaker to "CABLE Input (VB-Audio Virtual Cable)"
   - This routes Teams audio through VB-Cable to VoiceMeeter

### Step 4: Obsidian Configuration

1. **Obsidian Whisper Plugin Settings**
   - Set audio input to "VoiceMeeter Output (VB-Audio VoiceMeeter VAIO)"
   - This captures the mixed audio stream

## Audio Flow Diagram

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────┐
│ Microphone  │────▶│ VoiceMeeter      │────▶│ B1 Output   │
└─────────────┘     │ Hardware Input 1 │     │             │
                    └──────────────────┘     │ (Mixed      │
┌─────────────┐     ┌──────────────────┐     │  Audio)     │
│ Teams Audio │────▶│ VB-Cable         │────▶│             │
└─────────────┘     └──────────────────┘     │             │
                            │                 │             │
                            ▼                 │             │
                    ┌──────────────────┐     │             │
                    │ VoiceMeeter      │────▶│             │
                    │ Hardware Input 2 │     └─────────────┘
                    └──────────────────┘              │
                                                      ▼
                                              ┌─────────────┐
                                              │  Obsidian   │
                                              │  Whisper    │
                                              │  Plugin     │
                                              └─────────────┘
```

## Important Notes

1. **Single Mixed Track Output**
   - The recorded audio is a single stereo track with all sources mixed
   - Speaker separation requires post-processing diarization
   - This is why Obsidian Scribe includes pyannote.audio for speaker identification

2. **Audio Quality**
   - VoiceMeeter processes audio at high quality (up to 96kHz)
   - Ensure sample rates match across devices to avoid resampling artifacts

3. **Latency Considerations**
   - VoiceMeeter adds minimal latency (typically < 20ms)
   - Adjust buffer settings if you experience audio delays

## Troubleshooting

### No Audio from Teams
- Verify Teams speaker is set to "CABLE Input"
- Check that Hardware Input 2 in VoiceMeeter shows VB-Cable
- Ensure B1 is enabled on the correct strip

### Echo or Feedback
- Mute your speakers or use headphones during recording
- Disable "Monitor" on the microphone strip in VoiceMeeter

### Audio Drift or Sync Issues
- Ensure all devices use the same sample rate (48kHz recommended)
- In VoiceMeeter: Menu > System Settings > Preferred Main Sample Rate

### Obsidian Not Recording
- Restart Obsidian after changing audio devices
- Verify "VoiceMeeter Output" is the default recording device in Windows

## Best Practices

1. **Test Before Important Meetings**
   - Do a test recording to verify all audio sources are captured
   - Check levels to ensure balanced audio

2. **Monitor Audio Levels**
   - Keep VoiceMeeter open during recording to monitor levels
   - Aim for peaks around -12dB to -6dB

3. **Save VoiceMeeter Settings**
   - Menu > Save Settings
   - Load them after system restarts

## Integration with Obsidian Scribe

Once audio is recorded through this setup:

1. **File Location**: Audio files are saved to your Obsidian vault's Audio folder
2. **File Format**: Typically .wav or .mp3 depending on plugin settings
3. **Processing**: Obsidian Scribe monitors this folder and automatically:
   - Performs speaker diarization to separate mixed voices
   - Transcribes using the Whisper API
   - Generates formatted Markdown with speaker labels

This setup ensures all meeting participants are captured in a single file, which Obsidian Scribe can then process to create properly attributed transcripts.