import tkinter as tk
from tkinter import messagebox
import numpy as np
import simpleaudio as sa
from tkinter import ttk


class FrequencySweepApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Frequency Sweeper for IL Testing")
        self.geometry("360x280")

        self.frequency_start = tk.IntVar()
        self.frequency_end = tk.IntVar()
        self.frequency_step = tk.IntVar()
        self.tone_duration = tk.DoubleVar()
        self.delay_between_tones = tk.DoubleVar()

        self.create_widgets()
        self.frequency_window = None
        self.current_frequency_label = None
        self.time_remaining_label = None
        self.progress_bar = None
        self.stop_button = None
        self.is_sweep_running = False

    def create_widgets(self):
        frequency_frame = tk.LabelFrame(self, text="Frequency Settings")
        frequency_frame.pack(fill="both", expand=True, padx=10, pady=10)

        start_label = tk.Label(frequency_frame, text="Start Frequency (Hz):")
        start_label.grid(row=0, column=0, sticky="w")
        start_entry = tk.Entry(frequency_frame, textvariable=self.frequency_start)
        start_entry.grid(row=0, column=1)

        end_label = tk.Label(frequency_frame, text="End Frequency (Hz):")
        end_label.grid(row=1, column=0, sticky="w")
        end_entry = tk.Entry(frequency_frame, textvariable=self.frequency_end)
        end_entry.grid(row=1, column=1)

        step_label = tk.Label(frequency_frame, text="Frequency Step (Hz):")
        step_label.grid(row=2, column=0, sticky="w")
        step_entry = tk.Entry(frequency_frame, textvariable=self.frequency_step)
        step_entry.grid(row=2, column=1)

        duration_label = tk.Label(frequency_frame, text="Tone Duration (seconds):")
        duration_label.grid(row=3, column=0, sticky="w")
        duration_entry = tk.Entry(frequency_frame, textvariable=self.tone_duration)
        duration_entry.grid(row=3, column=1)

        delay_label = tk.Label(frequency_frame, text="Delay Between Tones (seconds):")
        delay_label.grid(row=4, column=0, sticky="w")
        delay_entry = tk.Entry(frequency_frame, textvariable=self.delay_between_tones)
        delay_entry.grid(row=4, column=1)

        start_button = tk.Button(self, text="Start Sweep", command=self.start_sweep)
        start_button.pack(pady=10)

        watermark_label = tk.Label(self, text="GitHub.com/AbhinavM2000", font=("Arial", 8), fg="gray")
        watermark_label.pack(side="bottom", pady=5)

    def start_sweep(self):
        if self.is_sweep_running:
            return

        start_frequency = self.frequency_start.get()
        end_frequency = self.frequency_end.get()
        frequency_step = self.frequency_step.get()
        tone_duration = self.tone_duration.get()
        delay_between_tones = self.delay_between_tones.get()

        if (
            start_frequency >= end_frequency
            or frequency_step <= 0
            or tone_duration <= 0
            or delay_between_tones <= 0
        ):
            messagebox.showerror("Invalid Parameters", "Please enter valid frequency, duration, and delay parameters.")
            return

        frequencies = np.arange(start_frequency, end_frequency + 1, frequency_step)

        total_iterations = len(frequencies)
        self.create_frequency_window()
        self.is_sweep_running = True
        self.stop_button.configure(state="normal")

        total_duration = total_iterations * (tone_duration + delay_between_tones)
        remaining_duration = total_duration

        for i, frequency in enumerate(frequencies):
            if not self.is_sweep_running:
                break

            self.update_frequency_window(frequency, remaining_duration, total_duration)
            tone = self.generate_tone(frequency, tone_duration)
            sa.play_buffer(tone, 1, 2, 44100).wait_done()

            if i != len(frequencies) - 1:
                self.update_frequency_window("Waiting...", remaining_duration, total_duration)
                self.after(int((tone_duration + delay_between_tones) * 1000),
                           self.update_frequency_window, frequency,
                           remaining_duration - tone_duration - delay_between_tones, total_duration)
                remaining_duration -= (tone_duration + delay_between_tones)

        self.update_frequency_window("Sweep Complete", 0, total_duration)
        self.stop_sweep()

    def create_frequency_window(self):
        self.frequency_window = tk.Toplevel()
        self.frequency_window.geometry("300x200")
        self.current_frequency_label = tk.Label(self.frequency_window, text="Current Frequency: ", font=("Arial", 12))
        self.current_frequency_label.pack(pady=10)
        self.time_remaining_label = tk.Label(self.frequency_window, text="Time Remaining: ", font=("Arial", 12))
        self.time_remaining_label.pack(pady=10)
        self.progress_bar = ttk.Progressbar(self.frequency_window, length=200, mode='determinate')
        self.progress_bar.pack(pady=10)
        self.stop_button = tk.Button(self.frequency_window, text="Stop", command=self.stop_sweep)
        self.stop_button.pack(pady=10)

    def update_frequency_window(self, frequency, remaining_duration, total_duration):
        if not self.is_sweep_running:
            return

        self.current_frequency_label.config(text=f"Current Frequency: {frequency} Hz")
        time_remaining = max(remaining_duration, 0)
        self.time_remaining_label.config(text=f"Time Remaining: {time_remaining:.2f} seconds")
        progress = (1 - remaining_duration / total_duration) * 100
        self.progress_bar['value'] = progress
        self.frequency_window.update()

    def stop_sweep(self):
        self.is_sweep_running = False
        self.stop_button.configure(state="disabled")
        self.progress_bar['value'] = 100
        self.current_frequency_label.config(text="Current Frequency: Sweep Complete")
        self.time_remaining_label.config(text="Time Remaining: 0.00 seconds")

    def generate_tone(self, frequency, duration):
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(2 * np.pi * frequency * t)
        return (tone * 32767).astype(np.int16)


if __name__ == "__main__":
    app = FrequencySweepApp()
    app.mainloop()
