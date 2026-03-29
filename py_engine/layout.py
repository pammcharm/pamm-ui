from __future__ import annotations


class LayoutManager:
    def layout_children(self, parent: "UIElement") -> None:
        flow_x = 16
        flow_y = 16
        max_row_height = 0

        for child in parent.children:
            if "x" in child.attrs or "y" in child.attrs:
                child.x = int(child.attrs.get("x", child.x))
                child.y = int(child.attrs.get("y", child.y))
            else:
                child.x = flow_x
                child.y = flow_y
                flow_y += child.height + 16
                max_row_height = max(max_row_height, child.height)

            child.update_absolute_position(parent.abs_x, parent.abs_y)
