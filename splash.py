import os
import sys
import tkinter as tk

from PIL import Image, ImageTk, ImageDraw

import launcher


# =========================================================
# RESOURCE PATH
# Works with Python and packaged PyInstaller EXE
# =========================================================

def resource_path(relative_path):

    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )

    return os.path.join(
        base_path,
        relative_path
    )


class SplashScreen:

    def __init__(self):

        self.root = tk.Tk()

        self.root.overrideredirect(True)

        self.root.configure(
            bg="#061B3A"
        )

        # Prevent main application from opening
        # when splash is closed manually
        self.user_closed = False

        # Used while restoring after minimization
        self.is_minimized = False

        # =================================================
        # FADE SETTINGS
        # =================================================

        self.alpha = 0.0

        self.root.attributes(
            "-alpha",
            self.alpha
        )

        self.is_fading_out = False

        # =================================================
        # ORIGINAL DESIGN SIZE
        # =================================================

        self.base_width = 1536
        self.base_height = 1024

        # =================================================
        # RESPONSIVE WINDOW SIZE
        # =================================================

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        available_width = screen_width - 60
        available_height = screen_height - 80

        scale_x = (
            available_width
            / self.base_width
        )

        scale_y = (
            available_height
            / self.base_height
        )

        self.scale = min(
            scale_x,
            scale_y,
            1
        )

        self.width = int(
            self.base_width
            * self.scale
        )

        self.height = int(
            self.base_height
            * self.scale
        )

        window_x = (
            screen_width
            - self.width
        ) // 2

        window_y = (
            screen_height
            - self.height
        ) // 2

        self.root.geometry(
            f"{self.width}x{self.height}"
            f"+{window_x}+{window_y}"
        )

        # =================================================
        # BACKGROUND IMAGE
        # =================================================

        image_path = resource_path(
            os.path.join(
                "assets",
                "splash_background.png"
            )
        )

        if not os.path.exists(image_path):

            raise FileNotFoundError(
                "Splash image not found:\n"
                f"{image_path}"
            )

        image = Image.open(
            image_path
        ).convert("RGB")

        image = image.resize(
            (
                self.width,
                self.height
            ),
            Image.Resampling.LANCZOS
        )

        # =================================================
        # REMOVE FAKE BUTTONS FROM BACKGROUND IMAGE
        # =================================================
        #
        # This covers the old minimize and close symbols
        # already drawn inside splash_background.png.
        #
        # Adjust these values only if the fake symbols are
        # located somewhere else in your image.
        # =================================================

        fake_controls_left = int(
            self.width - 150 * self.scale
        )

        fake_controls_top = 0

        fake_controls_right = self.width

        fake_controls_bottom = max(
            48,
            int(70 * self.scale)
        )

        draw = ImageDraw.Draw(image)

        draw.rectangle(
            (
                fake_controls_left,
                fake_controls_top,
                fake_controls_right,
                fake_controls_bottom
            ),
            fill="#061B3A"
        )

        self.background_image = (
            ImageTk.PhotoImage(image)
        )

        self.background_label = tk.Label(
            self.root,
            image=self.background_image,
            borderwidth=0,
            highlightthickness=0
        )

        self.background_label.place(
            x=0,
            y=0,
            width=self.width,
            height=self.height
        )

        # =================================================
        # REAL WINDOW CONTROL BUTTONS
        # =================================================

        button_width = max(
            34,
            int(46 * self.scale)
        )

        button_height = max(
            26,
            int(34 * self.scale)
        )

        button_font_size = max(
            11,
            int(16 * self.scale)
        )

        right_margin = max(
            14,
            int(22 * self.scale)
        )

        # Buttons moved slightly downward
        top_margin = max(
            20,
            int(30 * self.scale)
        )

        button_gap = max(
            5,
            int(8 * self.scale)
        )

        # -------------------------------------------------
        # CLOSE BUTTON
        # -------------------------------------------------

        self.close_button = tk.Button(
            self.root,
            text="✕",
            command=self.close_splash,
            font=(
                "Segoe UI",
                button_font_size,
                "bold"
            ),
            fg="white",
            bg="#C42B1C",
            activeforeground="white",
            activebackground="#E81123",
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            takefocus=False
        )

        self.close_button.place(
            x=(
                self.width
                - right_margin
                - button_width
            ),
            y=top_margin,
            width=button_width,
            height=button_height
        )

        # -------------------------------------------------
        # MINIMIZE BUTTON
        # -------------------------------------------------

        self.minimize_button = tk.Button(
            self.root,
            text="—",
            command=self.minimize_splash,
            font=(
                "Segoe UI",
                button_font_size,
                "bold"
            ),
            fg="white",
            bg="#102A50",
            activeforeground="white",
            activebackground="#244E7E",
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
            cursor="hand2",
            takefocus=False
        )

        self.minimize_button.place(
            x=(
                self.width
                - right_margin
                - button_width * 2
                - button_gap
            ),
            y=top_margin,
            width=button_width,
            height=button_height
        )

        self.minimize_button.lift()
        self.close_button.lift()

        # Close using Escape key
        self.root.bind(
            "<Escape>",
            lambda event: self.close_splash()
        )

        # Detect restoration from taskbar
        self.root.bind(
            "<Map>",
            self.restore_borderless_window
        )

        # =================================================
        # RESPONSIVE LOADING POSITIONS
        # =================================================

        self.loading_x = int(
            768 * self.scale
        )

        self.loading_text_y = int(
            885 * self.scale
        )

        self.loading_bar_y = int(
            935 * self.scale
        )

        # =================================================
        # LOADING TEXT
        # =================================================

        text_font_size = max(
            11,
            int(17 * self.scale)
        )

        self.loading_text = tk.Label(
            self.root,
            text="Initializing Application...",
            font=(
                "Segoe UI",
                text_font_size
            ),
            fg="white",
            bg="#061B3A"
        )

        self.loading_text.place(
            x=self.loading_x,
            y=self.loading_text_y,
            anchor="center"
        )

        # =================================================
        # LOADING BAR CANVAS
        # =================================================

        self.bar_width = int(
            760 * self.scale
        )

        self.bar_height = max(
            25,
            int(36 * self.scale)
        )

        self.loading_canvas = tk.Canvas(
            self.root,
            width=self.bar_width,
            height=self.bar_height + 12,
            bg="#061B3A",
            borderwidth=0,
            highlightthickness=0
        )

        self.loading_canvas.place(
            x=self.loading_x,
            y=self.loading_bar_y,
            anchor="center"
        )

        self.bar_top = 6

        self.bar_bottom = (
            self.bar_top
            + self.bar_height
        )

        self.bar_radius = (
            self.bar_height // 2
        )

        # Space reserved for percentage
        self.percentage_space = int(
            78 * self.scale
        )

        self.fill_max_width = (
            self.bar_width
            - self.percentage_space
            - 10
        )

        # =================================================
        # PERCENTAGE TEXT
        # =================================================

        percentage_font_size = max(
            10,
            int(14 * self.scale)
        )

        self.percentage_text = (
            self.loading_canvas.create_text(
                self.bar_width
                - int(39 * self.scale),

                self.bar_top
                + self.bar_height // 2,

                text="0%",
                fill="white",

                font=(
                    "Segoe UI",
                    percentage_font_size,
                    "bold"
                )
            )
        )

        # =================================================
        # LOADING MESSAGES
        # =================================================

        self.loading_messages = [
            (
                0,
                "Initializing Application..."
            ),
            (
                15,
                "Loading Configuration..."
            ),
            (
                30,
                "Connecting to Database..."
            ),
            (
                50,
                "Starting Flask Server..."
            ),
            (
                70,
                "Loading User Interface..."
            ),
            (
                85,
                "Preparing Desktop Application..."
            ),
            (
                100,
                "Application Ready"
            )
        ]

        self.progress = 0

        # =================================================
        # GLOW SETTINGS
        # =================================================

        self.glow_colors = [
            "#1F7BFF",
            "#3D9EFF",
            "#65BFFF",
            "#3D9EFF"
        ]

        self.glow_index = 0

        self.draw_progress_bar()

    # =====================================================
    # CLOSE SPLASH SCREEN
    # =====================================================

    def close_splash(self):

        if self.user_closed:
            return

        self.user_closed = True
        self.is_fading_out = True

        try:
            self.root.destroy()

        except tk.TclError:
            pass

    # =====================================================
    # MINIMIZE SPLASH SCREEN
    # =====================================================

    def minimize_splash(self):

        if self.user_closed:
            return

        self.is_minimized = True

        # Temporarily enable standard window management
        self.root.overrideredirect(False)

        self.root.iconify()

    # =====================================================
    # RESTORE BORDERLESS WINDOW
    # =====================================================

    def restore_borderless_window(
        self,
        event=None
    ):

        if (
            self.is_minimized
            and not self.user_closed
        ):

            self.is_minimized = False

            self.root.after(
                80,
                self.apply_borderless_mode
            )

    def apply_borderless_mode(self):

        if self.user_closed:
            return

        self.root.overrideredirect(True)

        self.root.lift()

        self.root.focus_force()

        self.minimize_button.lift()
        self.close_button.lift()

    # =====================================================
    # START SPLASH SCREEN
    # =====================================================

    def run(self):

        self.fade_in()

        self.root.after(
            250,
            self.animate_loading
        )

        self.root.after(
            100,
            self.animate_glow
        )

        self.root.mainloop()

    # =====================================================
    # FADE IN
    # =====================================================

    def fade_in(self):

        if self.user_closed:
            return

        if self.alpha < 1.0:

            self.alpha += 0.04

            self.alpha = min(
                self.alpha,
                1.0
            )

            self.root.attributes(
                "-alpha",
                self.alpha
            )

            self.root.after(
                15,
                self.fade_in
            )

    # =====================================================
    # FADE OUT
    # =====================================================

    def fade_out(self):

        if self.user_closed:
            return

        self.is_fading_out = True

        if self.alpha > 0.0:

            self.alpha -= 0.04

            self.alpha = max(
                self.alpha,
                0.0
            )

            self.root.attributes(
                "-alpha",
                self.alpha
            )

            self.root.after(
                15,
                self.fade_out
            )

        else:

            self.root.destroy()

            if not self.user_closed:
                launcher.start_app()

    # =====================================================
    # HEX COLOUR HELPERS
    # =====================================================

    @staticmethod
    def hex_to_rgb(hex_color):

        hex_color = hex_color.lstrip("#")

        return tuple(
            int(
                hex_color[index:index + 2],
                16
            )
            for index in (
                0,
                2,
                4
            )
        )

    @staticmethod
    def rgb_to_hex(rgb):

        return "#{:02x}{:02x}{:02x}".format(
            *rgb
        )

    def interpolate_colour(
        self,
        start_colour,
        end_colour,
        factor
    ):

        start_rgb = self.hex_to_rgb(
            start_colour
        )

        end_rgb = self.hex_to_rgb(
            end_colour
        )

        result = tuple(
            int(
                start_rgb[index]
                + (
                    end_rgb[index]
                    - start_rgb[index]
                ) * factor
            )
            for index in range(3)
        )

        return self.rgb_to_hex(
            result
        )

    # =====================================================
    # ROUNDED RECTANGLE
    # =====================================================

    def create_rounded_rectangle(
        self,
        x1,
        y1,
        x2,
        y2,
        radius,
        fill,
        outline="",
        width=1,
        tags=None
    ):

        points = [
            x1 + radius,
            y1,

            x2 - radius,
            y1,

            x2,
            y1,

            x2,
            y1 + radius,

            x2,
            y2 - radius,

            x2,
            y2,

            x2 - radius,
            y2,

            x1 + radius,
            y2,

            x1,
            y2,

            x1,
            y2 - radius,

            x1,
            y1 + radius,

            x1,
            y1
        ]

        return self.loading_canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=36,
            fill=fill,
            outline=outline,
            width=width,
            tags=tags
        )

    # =====================================================
    # DRAW PROGRESS BAR
    # =====================================================

    def draw_progress_bar(self):

        if self.user_closed:
            return

        self.loading_canvas.delete(
            "progress_graphics"
        )

        bar_left = 3

        bar_right = (
            self.bar_width - 3
        )

        bar_top = self.bar_top
        bar_bottom = self.bar_bottom
        radius = self.bar_radius

        glow_colour = (
            self.glow_colors[
                self.glow_index
            ]
        )

        # Soft glow border
        self.create_rounded_rectangle(
            bar_left,
            bar_top - 3,
            bar_right,
            bar_bottom + 3,
            radius + 3,
            fill="#061B3A",
            outline=glow_colour,
            width=2,
            tags="progress_graphics"
        )

        # Main loading bar background
        self.create_rounded_rectangle(
            bar_left,
            bar_top,
            bar_right,
            bar_bottom,
            radius,
            fill="#102A50",
            outline="#D9EAFF",
            width=2,
            tags="progress_graphics"
        )

        if self.progress > 0:

            fill_width = int(
                self.fill_max_width
                * self.progress
                / 100
            )

            fill_left = 6

            fill_right = (
                fill_left
                + fill_width
            )

            fill_top = (
                bar_top + 4
            )

            fill_bottom = (
                bar_bottom - 4
            )

            fill_height = (
                fill_bottom
                - fill_top
            )

            if fill_right < (
                fill_left
                + fill_height
            ):

                fill_right = (
                    fill_left
                    + fill_height
                )

            gradient_steps = max(
                10,
                min(
                    120,
                    fill_width
                )
            )

            start_colour = "#086BFF"
            end_colour = "#69C8FF"

            for step in range(
                gradient_steps
            ):

                factor = (
                    step
                    / max(
                        gradient_steps - 1,
                        1
                    )
                )

                colour = (
                    self.interpolate_colour(
                        start_colour,
                        end_colour,
                        factor
                    )
                )

                segment_left = (
                    fill_left
                    + int(
                        fill_width
                        * step
                        / gradient_steps
                    )
                )

                segment_right = (
                    fill_left
                    + int(
                        fill_width
                        * (step + 1)
                        / gradient_steps
                    )
                    + 1
                )

                self.loading_canvas.create_rectangle(
                    segment_left,
                    fill_top,
                    segment_right,
                    fill_bottom,
                    fill=colour,
                    outline="",
                    tags="progress_graphics"
                )

            # Rounded left edge
            self.loading_canvas.create_oval(
                fill_left,
                fill_top,
                fill_left + fill_height,
                fill_bottom,
                fill=start_colour,
                outline="",
                tags="progress_graphics"
            )

            # Rounded right edge
            self.loading_canvas.create_oval(
                fill_right - fill_height,
                fill_top,
                fill_right,
                fill_bottom,
                fill=end_colour,
                outline="",
                tags="progress_graphics"
            )

        self.loading_canvas.tag_raise(
            self.percentage_text
        )

    # =====================================================
    # CURRENT LOADING MESSAGE
    # =====================================================

    def get_loading_message(self):

        current_message = (
            self.loading_messages[0][1]
        )

        for progress_value, message in (
            self.loading_messages
        ):

            if self.progress >= progress_value:
                current_message = message

        return current_message

    # =====================================================
    # GLOW ANIMATION
    # =====================================================

    def animate_glow(self):

        if (
            self.is_fading_out
            or self.user_closed
        ):
            return

        self.glow_index += 1

        if self.glow_index >= len(
            self.glow_colors
        ):
            self.glow_index = 0

        self.draw_progress_bar()

        self.root.after(
            150,
            self.animate_glow
        )

    # =====================================================
    # LOADING ANIMATION
    # =====================================================

    def animate_loading(self):

        if self.user_closed:
            return

        if self.progress <= 100:

            self.loading_text.config(
                text=self.get_loading_message()
            )

            self.loading_canvas.itemconfig(
                self.percentage_text,
                text=f"{self.progress}%"
            )

            self.draw_progress_bar()

            self.progress += 1

            self.root.after(
                30,
                self.animate_loading
            )

        else:

            self.loading_text.config(
                text="Application Ready ✓"
            )

            self.loading_canvas.itemconfig(
                self.percentage_text,
                text="100%"
            )

            self.draw_progress_bar()

            self.root.after(
                500,
                self.open_application
            )

    # =====================================================
    # OPEN DESKTOP APPLICATION
    # =====================================================

    def open_application(self):

        if self.user_closed:
            return

        self.fade_out()


if __name__ == "__main__":

    SplashScreen().run()