import subprocess

from zenlog import log


def record_audio_auto_codec(input_stream_url):
    try:
        # Run FFprobe to get the audio codec information
        ffprobe_command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            input_stream_url,
        ]

        codec_info = subprocess.check_output(ffprobe_command, text=True)

        # Determine the file extension based on the audio codec
        audio_codec = codec_info.strip()
        audio_codec = audio_codec.split("\n")[0]
        return audio_codec

    except subprocess.CalledProcessError as e:
        log.error(f"Error: could not fetch codec {e}")
        return None


def record_audio_from_url(input_url, output_file, force_mp3, loglevel):
    """Deprecated: use start_recording_process instead (non-blocking)."""
    proc = start_recording_process(input_url, output_file, force_mp3, loglevel)
    if proc is None:
        log.error("Failed to start recorder")
        return
    proc.wait()
    log.info("Audio recorded successfully.")


def _build_ffmpeg_cmd(input_url, output_file, force_mp3, loglevel):
    cmd = [
        "ffmpeg",
        "-nostdin",      # no interactive stdin
        "-y",            # overwrite if exists
        "-i", input_url,
        "-vn",           # audio only
        # progress output to stdout (key=value lines)
        "-progress", "pipe:1",
        "-stats_period", "1",
    ]
    # codec
    cmd += ["-c:a", "libmp3lame" if force_mp3 else "copy"]
    # quiet unless debug
    if loglevel == "debug":
        cmd += ["-loglevel", "info"]
    else:
        cmd += ["-loglevel", "error", "-hide_banner"]
    cmd.append(output_file)
    return cmd


def start_recording_process(input_url, output_file, force_mp3, loglevel):
    """Start ffmpeg in background; returns Popen or None."""
    try:
        cmd = _build_ffmpeg_cmd(input_url, output_file, force_mp3, loglevel)
        # Silence output to keep UI clean (unless debug)
        # Always capture stdout for -progress parsing; suppress stderr unless debug
        stdout = subprocess.PIPE
        stderr = subprocess.PIPE if loglevel == "debug" else subprocess.DEVNULL
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=stderr,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        log.debug(f"Record start PID={proc.pid}")
        return proc
    except Exception as e:
        log.error(f"Failed to start recording: {e}")
        return None


def stop_recording_process(proc):
    try:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
    except Exception:
        pass
