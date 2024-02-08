import { DragOverlay, defaultDropAnimationSideEffects } from "@dnd-kit/core";

const dropAnimationConfig = {
  duration: 250 ,
  easing: "cubic-bezier(0.18, 0.67, 0.6, 1.22)",
  sideEffects: defaultDropAnimationSideEffects({
    styles: {
      active: {
        // opacity: "0.4",
      },
    },
  }),
};

export function SortableOverlay({ children }) {
  return (
    <DragOverlay dropAnimation={dropAnimationConfig}>{children}</DragOverlay>
  );
}
