"""
SEPTERIA Voice Feature Extraction Engine (Phase 8)
Signal processing and acoustic feature extraction using librosa, scipy, and numpy.

Privacy Invariant:
- Raw audio is processed in-memory and discarded by default.
- Only extracted numeric feature snapshots and quality metrics are returned.
- Non-diagnostic acoustic features: No single acoustic feature directly proves psychological stress.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
import io
import numpy as np
import scipy.signal
import soundfile as sf
import librosa

@dataclass
class VoiceFeatureSnapshot:
    timestamp: str
    feature_values: Dict[str, float]
    audio_quality_score: float
    speech_quality_score: float
    signal_duration_seconds: float
    evidence_status: str  # VALID, INCONCLUSIVE_DATA, POOR_AUDIO_QUALITY, NO_SPEECH_DETECTED
    processing_version: str = "v1.0.0-PROTOTYPE"
    quality_flags: List[str] = field(default_factory=list)

class VoiceFeatureExtractor:
    """
    Standard acoustic signal processing extractor for voluntary 20-30s voice check-ins.
    Extracts pitch (F0), temporal dynamics, energy metrics, spectral statistics, and MFCCs.
    """
    def __init__(
        self,
        min_duration_seconds: float = 5.0,
        max_duration_seconds: float = 45.0,
        min_snr_db: float = 6.0,
        target_sample_rate: int = 16000
    ):
        self.min_duration_seconds = min_duration_seconds
        self.max_duration_seconds = max_duration_seconds
        self.min_snr_db = min_snr_db
        self.target_sample_rate = target_sample_rate

    def validate_audio(self, audio: np.ndarray, sr: int) -> Tuple[bool, float, List[str]]:
        """
        Validates signal duration, amplitude, noise floor, clipping, and energy.
        Returns: (is_valid, quality_score, flags)
        """
        flags = []
        duration = len(audio) / float(sr)

        # 1. Duration check
        if duration < self.min_duration_seconds:
            flags.append(f"RECORDING_TOO_SHORT_{duration:.1f}S_MIN_{self.min_duration_seconds}S")
            return False, 0.2, flags
        if duration > self.max_duration_seconds:
            flags.append(f"RECORDING_EXCEEDED_MAX_{duration:.1f}S")

        # 2. Silence / Energy check
        rms = np.sqrt(np.mean(audio**2) + 1e-12)
        if rms < 0.005:
            flags.append("SIGNAL_TOO_FAINT_OR_SILENT")
            return False, 0.1, flags

        # 3. Clipping check
        clipping_ratio = np.sum(np.abs(audio) >= 0.98) / float(len(audio))
        if clipping_ratio > 0.05:
            flags.append("EXCESSIVE_AUDIO_CLIPPING_DETECTED")

        # 4. SNR Proxy (Signal-to-Noise Ratio proxy via percentile ratio)
        frame_energies = librosa.feature.rms(y=audio, frame_length=512, hop_length=256)[0]
        p90_energy = np.percentile(frame_energies, 90) + 1e-12
        p10_energy = np.percentile(frame_energies, 10) + 1e-12
        snr_proxy_db = 20.0 * np.log10(p90_energy / p10_energy)

        if snr_proxy_db < self.min_snr_db:
            flags.append("HIGH_BACKGROUND_NOISE_POOR_SNR")

        # Compute continuous quality score [0.0, 1.0]
        quality = 1.0
        if clipping_ratio > 0.01:
            quality -= min(0.3, clipping_ratio * 10)
        if snr_proxy_db < 15.0:
            quality -= max(0.0, (15.0 - snr_proxy_db) / 20.0)
        if duration < 10.0:
            quality -= 0.15

        quality_score = float(np.clip(quality, 0.1, 1.0))
        is_valid = len([f for f in flags if "TOO_SHORT" in f or "SILENT" in f]) == 0 and quality_score >= 0.35

        return is_valid, quality_score, flags

    def extract_features(
        self,
        audio_data: bytes,
        sample_rate: Optional[int] = None
    ) -> VoiceFeatureSnapshot:
        """
        Parses raw wav/ogg/flac audio bytes, validates signal quality, and extracts acoustic markers.
        """
        now_ts = datetime.utcnow().isoformat()
        try:
            with sf.SoundFile(io.BytesIO(audio_data)) as sound_file:
                audio = sound_file.read(dtype="float32")
                sr = sound_file.samplerate
                
                # Convert multi-channel to mono
                if len(audio.shape) > 1:
                    audio = np.mean(audio, axis=1)
        except Exception as e:
            return VoiceFeatureSnapshot(
                timestamp=now_ts,
                feature_values={},
                audio_quality_score=0.0,
                speech_quality_score=0.0,
                signal_duration_seconds=0.0,
                evidence_status="POOR_AUDIO_QUALITY",
                quality_flags=[f"AUDIO_DECODING_ERROR: {str(e)}"]
            )

        # Resample if needed
        if sr != self.target_sample_rate:
            audio = librosa.resample(y=audio, orig_sr=sr, target_sr=self.target_sample_rate)
            sr = self.target_sample_rate

        # Quality validation
        is_valid, quality_score, quality_flags = self.validate_audio(audio, sr)
        duration = len(audio) / float(sr)

        if not is_valid:
            return VoiceFeatureSnapshot(
                timestamp=now_ts,
                feature_values={},
                audio_quality_score=quality_score,
                speech_quality_score=0.2,
                signal_duration_seconds=float(duration),
                evidence_status="INCONCLUSIVE_DATA",
                quality_flags=quality_flags
            )

        # 1. Fundamental Frequency (F0 / Pitch) via PYIN
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz('C2'),
            fmax=librosa.note_to_hz('C7'),
            sr=sr,
            frame_length=2048,
            hop_length=512
        )
        voiced_f0 = f0[voiced_flag & ~np.isnan(f0)] if f0 is not None else np.array([])

        if len(voiced_f0) > 5:
            f0_mean = float(np.mean(voiced_f0))
            f0_std = float(np.std(voiced_f0))
            f0_iqr = float(np.percentile(voiced_f0, 75) - np.percentile(voiced_f0, 25))
            voiced_ratio = float(len(voiced_f0) / len(f0))
        else:
            f0_mean = 120.0
            f0_std = 15.0
            f0_iqr = 12.0
            voiced_ratio = 0.1
            quality_flags.append("LOW_VOICED_SEGMENT_DENSITY")

        # 2. Energy & Dynamics
        rms_frames = librosa.feature.rms(y=audio, frame_length=1024, hop_length=512)[0]
        rms_mean = float(np.mean(rms_frames))
        rms_std = float(np.std(rms_frames))
        rms_range = float(np.percentile(rms_frames, 95) - np.percentile(rms_frames, 5))

        # 3. Speech Rate & Pause Dynamics (Voice Activity Detection proxy)
        speech_thresh = np.percentile(rms_frames, 35)
        speech_mask = rms_frames > speech_thresh
        speech_ratio = float(np.mean(speech_mask))
        pause_ratio = float(1.0 - speech_ratio)

        # Count pause segments and durations
        pauses = []
        curr_pause = 0
        hop_duration = 512.0 / sr
        for is_speech in speech_mask:
            if not is_speech:
                curr_pause += hop_duration
            else:
                if curr_pause > 0.15:  # Min pause threshold 150ms
                    pauses.append(curr_pause)
                curr_pause = 0
        if curr_pause > 0.15:
            pauses.append(curr_pause)

        mean_pause_duration = float(np.mean(pauses)) if len(pauses) > 0 else 0.0
        speech_rate_proxy = float(len(pauses) / max(1.0, duration / 60.0))  # Syllable/pause bursts per minute

        # 4. Spectral Statistics
        spec_cent = librosa.feature.spectral_centroid(y=audio, sr=sr, hop_length=512)[0]
        spec_bw = librosa.feature.spectral_bandwidth(y=audio, sr=sr, hop_length=512)[0]
        zcr = librosa.feature.zero_crossing_rate(y=audio, hop_length=512)[0]

        spec_centroid_mean = float(np.mean(spec_cent))
        spec_centroid_std = float(np.std(spec_cent))
        spec_bandwidth_mean = float(np.mean(spec_bw))
        zcr_mean = float(np.mean(zcr))

        # 5. MFCC Statistics (13 coefficients)
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13, hop_length=512)
        mfcc_means = {f"mfcc_{i+1}_mean": float(np.mean(mfcc[i])) for i in range(13)}
        mfcc_stds = {f"mfcc_{i+1}_std": float(np.std(mfcc[i])) for i in range(13)}

        features = {
            "f0_mean": f0_mean,
            "f0_std": f0_std,
            "f0_iqr": f0_iqr,
            "voiced_ratio": voiced_ratio,
            "speech_ratio": speech_ratio,
            "pause_ratio": pause_ratio,
            "mean_pause_duration_s": mean_pause_duration,
            "speech_rate_proxy_bpm": speech_rate_proxy,
            "rms_energy_mean": rms_mean,
            "rms_energy_std": rms_std,
            "rms_dynamic_range": rms_range,
            "spectral_centroid_mean": spec_centroid_mean,
            "spectral_centroid_std": spec_centroid_std,
            "spectral_bandwidth_mean": spec_bandwidth_mean,
            "zero_crossing_rate_mean": zcr_mean,
            **mfcc_means,
            **mfcc_stds,
        }

        speech_quality_score = float(np.clip(quality_score * (0.5 + 0.5 * voiced_ratio), 0.2, 1.0))

        return VoiceFeatureSnapshot(
            timestamp=now_ts,
            feature_values=features,
            audio_quality_score=quality_score,
            speech_quality_score=speech_quality_score,
            signal_duration_seconds=float(duration),
            evidence_status="VALID",
            quality_flags=quality_flags
        )

    @staticmethod
    def generate_synthetic_audio(
        duration_seconds: float = 20.0,
        pitch_f0_hz: float = 125.0,
        speech_rate_multiplier: float = 1.0,
        energy_level: float = 0.25,
        noise_level: float = 0.01,
        sample_rate: int = 16000
    ) -> bytes:
        """
        Synthesizes a controlled audio WAV byte array for deterministic testing and demo scenarios.
        """
        n_samples = int(duration_seconds * sample_rate)
        t = np.linspace(0, duration_seconds, n_samples, endpoint=False)

        # Formant/harmonic harmonic voice synthesis
        fundamental = np.sin(2 * np.pi * pitch_f0_hz * t)
        h2 = 0.5 * np.sin(2 * np.pi * pitch_f0_hz * 2.0 * t)
        h3 = 0.25 * np.sin(2 * np.pi * pitch_f0_hz * 3.0 * t)
        signal = (fundamental + h2 + h3) * energy_level

        # Modulate with speech-like syllable envelope (e.g. 4 Hz burst cadence * multiplier)
        syllable_rate = 3.8 * speech_rate_multiplier
        envelope = 0.5 * (1.0 + np.sin(2 * np.pi * syllable_rate * t))
        envelope = np.clip(envelope ** 1.5, 0.05, 1.0)
        signal = signal * envelope

        # Add Gaussian noise floor
        noise = np.random.normal(0, noise_level, n_samples)
        signal = np.clip(signal + noise, -0.95, 0.95).astype(np.float32)

        out_io = io.BytesIO()
        sf.write(out_io, signal, sample_rate, format='WAV', subtype='PCM_16')
        return out_io.getvalue()
