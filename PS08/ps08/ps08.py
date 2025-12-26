import os, math, struct
from copy import deepcopy
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


SHAPE_TYPE_NAMES = {
    0: "null shape",
    1: "point",
    3: "polyline",
    5: "polygon",
    8: "multipoint",
    11: "point Z",
    13: "polyline Z",
    15: "polygon Z",
    18: "multipoint Z",
    21: "point M",
    23: "polyline M",
    25: "polygon M",
    28: "multipoint M",
}


class ShapefileFormatError(Exception):
    pass


class ShapefileReader:
    def __init__(self, path: str):
        self.path = path
        self.shape_type = None
        self.records = []

    def read(self) -> None:
        with open(self.path, "rb") as f:
            header = f.read(100)
            if len(header) < 100:
                raise ShapefileFormatError("header too short")
            self._parse_header(header)
            self._read_records(f)

    def _parse_header(self, header: bytes) -> None:
        file_code = struct.unpack(">i", header[0:4])[0]
        if file_code != 9994:
            raise ShapefileFormatError("invalid file code")
        version, shp_type = struct.unpack("<2i", header[28:36])
        if version != 1000:
            raise ShapefileFormatError("invalid version")
        self.shape_type = shp_type

    def _read_records(self, f) -> None:
        while True:
            rh = f.read(8)
            if len(rh) == 0:
                break
            if len(rh) < 8:
                raise ShapefileFormatError("record header too short")
            _, content_len_words = struct.unpack(">2i", rh)
            content = f.read(content_len_words * 2)
            if len(content) < content_len_words * 2:
                raise ShapefileFormatError("record content too short")

            st = struct.unpack("<i", content[0:4])[0]
            rec = {"shape_type": st}

            if st == 0:
                self.records.append(rec)
                continue

            if st in (1, 21):
                x, y = struct.unpack("<2d", content[4:20])
                rec["points"] = [(x, y)]
                self.records.append(rec)
                continue

            if st == 11:
                x, y, z = struct.unpack("<3d", content[4:28])
                rec["points"] = [(x, y)]
                rec["z"] = [z]
                self.records.append(rec)
                continue

            if st in (8, 28):
                n = struct.unpack("<i", content[36:40])[0]
                pts, off = [], 40
                for _ in range(n):
                    x, y = struct.unpack("<2d", content[off:off + 16])
                    pts.append((x, y))
                    off += 16
                rec["points"] = pts
                self.records.append(rec)
                continue

            if st == 18:
                n = struct.unpack("<i", content[36:40])[0]
                pts, off = [], 40
                for _ in range(n):
                    x, y = struct.unpack("<2d", content[off:off + 16])
                    pts.append((x, y))
                    off += 16
                off += 16
                zs = []
                for _ in range(n):
                    (z,) = struct.unpack("<d", content[off:off + 8])
                    zs.append(z)
                    off += 8
                rec["points"] = pts
                rec["z"] = zs
                self.records.append(rec)
                continue

            if st in (3, 5, 23, 25):
                num_parts, num_points = struct.unpack("<2i", content[36:44])
                parts_idx = list(struct.unpack(f"<{num_parts}i", content[44:44 + 4 * num_parts]))
                pts, off = [], 44 + 4 * num_parts
                for _ in range(num_points):
                    x, y = struct.unpack("<2d", content[off:off + 16])
                    pts.append((x, y))
                    off += 16
                parts = []
                for i in range(num_parts):
                    a = parts_idx[i]
                    b = parts_idx[i + 1] if i + 1 < num_parts else num_points
                    parts.append(pts[a:b])
                rec["parts"] = parts
                self.records.append(rec)
                continue

            if st in (13, 15):
                num_parts, num_points = struct.unpack("<2i", content[36:44])
                parts_idx = list(struct.unpack(f"<{num_parts}i", content[44:44 + 4 * num_parts]))
                pts, off = [], 44 + 4 * num_parts
                for _ in range(num_points):
                    x, y = struct.unpack("<2d", content[off:off + 16])
                    pts.append((x, y))
                    off += 16
                off += 16
                zs = []
                for _ in range(num_points):
                    (z,) = struct.unpack("<d", content[off:off + 8])
                    zs.append(z)
                    off += 8
                parts, z_parts = [], []
                for i in range(num_parts):
                    a = parts_idx[i]
                    b = parts_idx[i + 1] if i + 1 < num_parts else num_points
                    parts.append(pts[a:b])
                    z_parts.append(zs[a:b])
                rec["parts"] = parts
                rec["z_parts"] = z_parts
                self.records.append(rec)
                continue

            raise ShapefileFormatError(f"unsupported record type: {st}")


def _extent_xy_from_records(records):
    xs, ys = [], []
    for rec in records:
        if rec.get("shape_type", 0) == 0:
            continue
        for x, y in rec.get("points", []):
            xs.append(x)
            ys.append(y)
        for part in rec.get("parts", []):
            for x, y in part:
                xs.append(x)
                ys.append(y)
    return xs, ys


def _smart_figsize(xs, ys, base=7.0):
    if not xs or not ys:
        return (base, base)
    dx = max(xs) - min(xs)
    dy = max(ys) - min(ys)
    if dx <= 0:
        dx = 1.0
    if dy <= 0:
        dy = 1.0
    r = dx / dy
    w = base * min(2.2, max(0.8, r))
    h = base * min(2.2, max(0.8, 1.0 / r))
    return (w, h)


def _apply_axis(ax, xs, ys):
    if xs and ys:
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        dx = xmax - xmin
        dy = ymax - ymin
        if dx == 0:
            dx = 1.0
        if dy == 0:
            dy = 1.0
        mx = dx * 0.05
        my = dy * 0.05
        ax.set_xlim(xmin - mx, xmax + mx)
        ax.set_ylim(ymin - my, ymax + my)
    ax.set_aspect("equal", adjustable="box")
    ax.ticklabel_format(style="plain", useOffset=False)


def _close_ring(ring):
    if not ring:
        return ring
    return ring if ring[0] == ring[-1] else ring + [ring[0]]


def plot_shapefile(reader):
    st = reader.shape_type
    xs, ys = _extent_xy_from_records(reader.records)
    fig, ax = plt.subplots(figsize=_smart_figsize(xs, ys))

    if st in (1, 8, 21, 28):
        px, py = [], []
        for rec in reader.records:
            if rec.get("shape_type", 0) == 0:
                continue
            for x, y in rec.get("points", []):
                px.append(x)
                py.append(y)
        ax.scatter(px, py, s=10)
        _apply_axis(ax, px, py)
        ax.set_title("Points")
        plt.tight_layout()
        plt.show()
        return

    if st in (3, 23):
        for rec in reader.records:
            if rec.get("shape_type", 0) == 0:
                continue
            for part in rec.get("parts", []):
                if not part:
                    continue
                ax.plot([p[0] for p in part], [p[1] for p in part])
        _apply_axis(ax, xs, ys)
        ax.set_title("Polylines")
        plt.tight_layout()
        plt.show()
        return

    if st in (5, 25):
        for rec in reader.records:
            if rec.get("shape_type", 0) == 0:
                continue
            verts, codes = [], []
            for ring in rec.get("parts", []):
                ring = _close_ring(ring)
                if len(ring) < 4:
                    continue
                verts.append(ring[0])
                codes.append(Path.MOVETO)
                for pt in ring[1:]:
                    verts.append(pt)
                    codes.append(Path.LINETO)
                verts.append(ring[0])
                codes.append(Path.CLOSEPOLY)
            if verts:
                path = Path(verts, codes)
                patch = PathPatch(path, facecolor="lightgray", edgecolor="black", lw=1, alpha=0.6)
                try:
                    patch.set_fillrule("evenodd")
                except Exception:
                    pass
                ax.add_patch(patch)

        _apply_axis(ax, xs, ys)
        ax.set_title("Polygons (holes supported)")
        plt.tight_layout()
        plt.show()
        return

    plt.close(fig)

    if st in (11, 18):
        px, py, pz = [], [], []
        for rec in reader.records:
            if rec.get("shape_type", 0) == 0:
                continue
            pts = rec.get("points", [])
            zs = rec.get("z", [])
            for i, (x, y) in enumerate(pts):
                px.append(x)
                py.append(y)
                pz.append(zs[i] if i < len(zs) else 0.0)
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        ax.scatter(px, py, pz, s=10)
        ax.set_title("Points (3D)")
        plt.show()
        return

    if st == 13:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        for rec in reader.records:
            if rec.get("shape_type", 0) == 0:
                continue
            parts = rec.get("parts", [])
            z_parts = rec.get("z_parts", [])
            for i, part in enumerate(parts):
                if not part:
                    continue
                zs = z_parts[i] if i < len(z_parts) else [0.0] * len(part)
                ax.plot([p[0] for p in part], [p[1] for p in part], zs)
        ax.set_title("Polylines (3D)")
        plt.show()
        return

    if st == 15:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        for rec in reader.records:
            if rec.get("shape_type", 0) == 0:
                continue
            parts = rec.get("parts", [])
            z_parts = rec.get("z_parts", [])
            for i, ring in enumerate(parts):
                ring = _close_ring(ring)
                zs = z_parts[i] if i < len(z_parts) else [0.0] * len(ring)
                verts3d = [(ring[j][0], ring[j][1], zs[j] if j < len(zs) else 0.0) for j in range(len(ring))]
                poly = Poly3DCollection([verts3d], alpha=0.3)
                ax.add_collection3d(poly)
        ax.set_title("Polygons (3D)")
        plt.show()
        return

    fig, ax = plt.subplots()
    ax.set_title(f"Unsupported plot type: {st}")
    plt.show()


def transform_xy(x, y, dx, dy, angle_deg):
    t = math.radians(angle_deg)
    c, s = math.cos(t), math.sin(t)
    return x * c - y * s + dx, x * s + y * c + dy


def transform_records(records, dx, dy, angle_deg):
    out = deepcopy(records)
    for rec in out:
        if rec.get("shape_type", 0) == 0:
            continue
        if "points" in rec and rec.get("parts") is None:
            rec["points"] = [transform_xy(x, y, dx, dy, angle_deg) for x, y in rec["points"]]
            continue
        if "parts" in rec:
            rec["parts"] = [[transform_xy(x, y, dx, dy, angle_deg) for x, y in part] for part in rec["parts"]]
        rec.pop("box", None)
    return out


def _bbox_xy(points):
    if not points:
        return 0.0, 0.0, 0.0, 0.0
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def _build_shp_header(file_len_words, shp_type, bbox):
    xmin, ymin, xmax, ymax = bbox
    h = bytearray(100)
    struct.pack_into(">i", h, 0, 9994)
    struct.pack_into(">i", h, 24, file_len_words)
    struct.pack_into("<i", h, 28, 1000)
    struct.pack_into("<i", h, 32, shp_type)
    struct.pack_into("<4d", h, 36, xmin, ymin, xmax, ymax)
    struct.pack_into("<4d", h, 68, 0.0, 0.0, 0.0, 0.0)
    return bytes(h)


def write_shp_only(out_path, shp_type, records):
    contents = []
    all_xy = []

    for rec in records:
        st = rec.get("shape_type", 0)

        if st == 0:
            content = struct.pack("<i", 0)

        elif shp_type == 1:
            pts = rec.get("points") or []
            if not pts:
                content = struct.pack("<i", 0)
            else:
                x, y = pts[0]
                all_xy.append((x, y))
                content = struct.pack("<i2d", 1, x, y)

        elif shp_type in (3, 5):
            parts = rec.get("parts") or []
            flat = [pt for part in parts for pt in part]
            all_xy.extend(flat)

            if not flat:
                content = struct.pack("<i", 0)
            else:
                parts_idx = []
                cur = 0
                for part in parts:
                    parts_idx.append(cur)
                    cur += len(part)

                xmin, ymin, xmax, ymax = _bbox_xy(flat)
                buf = bytearray()
                buf += struct.pack("<i", shp_type)
                buf += struct.pack("<4d", xmin, ymin, xmax, ymax)
                buf += struct.pack("<2i", len(parts), len(flat))
                buf += struct.pack(f"<{len(parts_idx)}i", *parts_idx)
                for x, y in flat:
                    buf += struct.pack("<2d", x, y)
                content = bytes(buf)

        else:
            raise ValueError("Only Point(1), PolyLine(3), Polygon(5) are supported for output.")

        if len(content) % 2 != 0:
            raise ValueError("Record content length must be even.")
        contents.append(content)

    file_bytes = 100 + sum(8 + len(c) for c in contents)
    header = _build_shp_header(file_bytes // 2, shp_type, _bbox_xy(all_xy))

    with open(out_path, "wb") as f:
        f.write(header)
        for i, c in enumerate(contents, start=1):
            f.write(struct.pack(">2i", i, len(c) // 2))
            f.write(c)


def main():
    root = tk.Tk()
    root.withdraw()

    shp_in = filedialog.askopenfilename(
        title="Select shapefile (.shp)",
        filetypes=[("Shapefile", "*.shp"), ("All files", "*.*")]
    )
    if not shp_in:
        return
    if not shp_in.lower().endswith(".shp"):
        print("Invalid input file.")
        return

    try:
        reader = ShapefileReader(shp_in)
        reader.read()
    except Exception as e:
        print("Read error:", e)
        return

    st = reader.shape_type
    print("Input type:", SHAPE_TYPE_NAMES.get(st, "unknown"), f"({st})")

    if st not in (1, 3, 5):
        messagebox.showerror(
            "Unsupported shapefile type",
            f"This tool only supports Point(1), PolyLine(3), Polygon(5).\nSelected: {SHAPE_TYPE_NAMES.get(st, 'unknown')} ({st})"
        )
        return

    plot_shapefile(reader)

    dx = simpledialog.askfloat("Shift", "dx:", initialvalue=0.0)
    if dx is None:
        return
    dy = simpledialog.askfloat("Shift", "dy:", initialvalue=0.0)
    if dy is None:
        return
    ang = simpledialog.askfloat("Rotation", "angle (deg, CCW +):", initialvalue=0.0)
    if ang is None:
        return

    print(f"Shift: dx={dx}, dy={dy}")
    print(f"Rotation: angle={ang} degrees (CCW positive)")

    base = os.path.splitext(os.path.basename(shp_in))[0]
    shp_out = filedialog.asksaveasfilename(
        title="Save transformed shapefile (.shp)",
        defaultextension=".shp",
        initialfile=base + "_transformed.shp",
        filetypes=[("Shapefile", "*.shp")]
    )
    if not shp_out:
        return

    try:
        new_records = transform_records(reader.records, dx, dy, ang)
        write_shp_only(shp_out, st, new_records)
    except Exception as e:
        print("Write error:", e)
        return

    print("Saved:", shp_out)

    try:
        out_reader = ShapefileReader(shp_out)
        out_reader.read()
        plot_shapefile(out_reader)
    except Exception as e:
        print("Output read/plot error:", e)


if __name__ == "__main__":
    main()