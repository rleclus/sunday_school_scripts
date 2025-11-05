import tkinter as tk
import math
import sys
import subprocess

class BalancingScaleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Balancing Scale")

        self.canvas = tk.Canvas(root, width=800, height=520, bg="white")
        self.canvas.pack()

        # totals and state
        self.current_angle = 0.0
        self.target_angle = 0.0
        self.animating = False

        # allow multiple instances of the same weight
        # each placed weight is a dict: {'id': int, 'value': int}
        self.active_left = []
        self.active_right = []
        self.next_instance_id = 1  # unique id for each placed weight

        # simple palette values
        self.weights_left = [i for i in range(1, 11)]
        self.weights_right = [i for i in range(1, 11)]

        # pivot for beam drawing
        self.pivot_x = 400
        self.pivot_y = 250
        self.beam = None

        # draw UI
        self.draw_base()
        self.draw_weights_palette()
        self.add_reset_button()
        self.title_text = self.canvas.create_text(400, 30, text="L=0 | R=0", font=("Arial", 16, "bold"))

        self.draw_beam(0)  # initial balanced beam

    # ---------------- UI / Drawing ----------------

    def draw_base(self):
        # stand
        self.canvas.create_rectangle(390, 250, 410, 400, fill="black")
        self.canvas.create_rectangle(350, 400, 450, 420, fill="black")

    def draw_weights_palette(self):
        """Palette on left/right - clicking these adds a new instance to that side."""
        # left palette
        for i, w in enumerate(self.weights_left):
            x = 100
            y = 60 + i * 40
            tag = f"palette_left_{i}"
            self.canvas.create_oval(x-18, y-18, x+18, y+18, fill="lightblue", tags=tag)
            self.canvas.create_text(x, y, text=str(w), tags=tag)
            # bind palette clicks -> add a new instance
            self.canvas.tag_bind(tag, "<Button-1>", lambda e, side="left", value=w: self.add_weight_instance(side, value))

        # right palette
        for i, w in enumerate(self.weights_right):
            x = 700
            y = 60 + i * 40
            tag = f"palette_right_{i}"
            self.canvas.create_oval(x-18, y-18, x+18, y+18, fill="lightcoral", tags=tag)
            self.canvas.create_text(x, y, text=str(w), tags=tag)
            self.canvas.tag_bind(tag, "<Button-1>", lambda e, side="right", value=w: self.add_weight_instance(side, value))

    def add_reset_button(self):
        btn = tk.Button(self.root, text="Reset", font=("Arial", 12), command=self.reset_scale)
        btn.pack(pady=8)

    def draw_beam(self, angle):
        """
        Draw the beam rotated around pivot_x,pivot_y.
        Note: angle sign chosen so positive angle => LEFT side down.
        """
        # clear previous beam, plates and placed weights
        if self.beam:
            self.canvas.delete(self.beam)
        self.canvas.delete("plate")
        self.canvas.delete("placed_weight")  # tags for drawn weights on plates

        length = 300
        left_x = self.pivot_x - length / 2
        right_x = self.pivot_x + length / 2

        # offset: positive angle -> left down (y increases downwards on canvas)
        offset = math.tan(math.radians(angle)) * (length / 2)

        left_y = self.pivot_y + offset
        right_y = self.pivot_y - offset

        self.beam = self.canvas.create_line(left_x, left_y, right_x, right_y, width=6, fill="saddlebrown")

        # plates
        self.canvas.create_oval(left_x - 40, left_y + 10, left_x + 40, left_y + 30, fill="goldenrod", tags="plate")
        self.canvas.create_oval(right_x - 40, right_y + 10, right_x + 40, right_y + 30, fill="goldenrod", tags="plate")

        # draw each placed weight on its plate
        for idx, inst in enumerate(self.active_left):
            self._draw_placed_weight(left_x, left_y, idx, inst, side="left")
        for idx, inst in enumerate(self.active_right):
            self._draw_placed_weight(right_x, right_y, idx, inst, side="right")

    def _draw_placed_weight(self, plate_x, plate_y, index_on_plate, instance, side):
        """
        Draw a single placed weight. index_on_plate staggers vertically so multiple weights are visible.
        Each placed weight has a unique tag so it can be removed by clicking it.
        """
        offset_y = -18 * index_on_plate  # stack upwards so they don't overlap completely
        value = instance['value']
        iid = instance['id']
        tag = f"placed_{side}_{iid}"
        color = "lightblue" if side == "left" else "lightcoral"

        x0 = plate_x - 12
        y0 = plate_y - 28 + offset_y
        x1 = plate_x + 12
        y1 = plate_y - 8 + offset_y

        self.canvas.create_oval(x0, y0, x1, y1, fill=color, tags=("placed_weight", tag))
        self.canvas.create_text(plate_x, plate_y - 18 + offset_y, text=str(value), tags=("placed_weight", tag))
        # bind click on placed weight -> remove that specific instance
        self.canvas.tag_bind(tag, "<Button-1>", lambda e, side=side, iid=iid: self.remove_weight_instance(side, iid))

    # ---------------- Logic: add/remove/reset ----------------

    def add_weight_instance(self, side, value):
        """Add a new weight instance to the chosen side (multiple allowed)."""
        instance = {'id': self.next_instance_id, 'value': int(value)}
        self.next_instance_id += 1

        if side == "left":
            self.active_left.append(instance)
        else:
            self.active_right.append(instance)

        self.update_totals_and_scale()

    def remove_weight_instance(self, side, instance_id):
        """Remove a previously placed instance identified by its unique id."""
        if side == "left":
            self.active_left = [inst for inst in self.active_left if inst['id'] != instance_id]
        else:
            self.active_right = [inst for inst in self.active_right if inst['id'] != instance_id]

        self.update_totals_and_scale()

    def reset_scale(self):
        self.active_left.clear()
        self.active_right.clear()
        self.target_angle = 0.0
        # ensure quick animation to center
        if not self.animating:
            self.animate_tilt()
        self.canvas.itemconfig(self.title_text, text="L=0 | R=0")

    # ---------------- Totals & animation ----------------

    def update_totals_and_scale(self):
        left_total = sum(inst['value'] for inst in self.active_left)
        right_total = sum(inst['value'] for inst in self.active_right)
        # update UI text
        self.canvas.itemconfig(self.title_text, text=f"L={left_total} | R={right_total}")

        # Important: angle positive => LEFT side down.
        # target_angle = left_total - right_total (clamped).
        diff = left_total - right_total
        self.target_angle = max(-15.0, min(15.0, diff))
        if not self.animating:
            self.animate_tilt()

    def animate_tilt(self):
        """Smoothly ease current_angle toward target_angle."""
        self.animating = True
        # easing factor
        step = (self.target_angle - self.current_angle) * 0.20
        if abs(step) < 0.05:
            self.current_angle = self.target_angle
            self.draw_beam(self.current_angle)
            self.animating = False
            return

        self.current_angle += step
        self.draw_beam(self.current_angle)
        # schedule next frame (~33 FPS)
        self.root.after(30, self.animate_tilt)

# ---------------- Helper to ensure Tkinter (best-effort) ----------------

def ensure_tkinter():
    try:
        import tkinter  # noqa
    except ImportError:
        print("Tkinter not installed. Attempting to install on Linux using apt...")
        if sys.platform.startswith("linux"):
            subprocess.call(["sudo", "apt-get", "update"])
            subprocess.call(["sudo", "apt-get", "install", "-y", "python3-tk"])
        else:
            print("On macOS/Windows Tkinter usually comes with Python. Please install Python from python.org or your package manager.")

# ---------------- Run ----------------

if __name__ == "__main__":
    ensure_tkinter()
    root = tk.Tk()
    app = BalancingScaleApp(root)
    root.mainloop()
