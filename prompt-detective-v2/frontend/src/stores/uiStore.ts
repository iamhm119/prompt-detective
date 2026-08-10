import { create } from 'zustand';

export type TutorialTrigger = 'auto' | 'dashboard' | 'navbar' | 'cta';

interface UiState {
  isTutorialOpen: boolean;
  tutorialTrigger: TutorialTrigger | null;
  openTutorial: (trigger?: TutorialTrigger) => void;
  closeTutorial: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  isTutorialOpen: false,
  tutorialTrigger: null,
  openTutorial: (trigger) =>
    set({
      isTutorialOpen: true,
      tutorialTrigger: trigger ?? null,
    }),
  closeTutorial: () =>
    set({
      isTutorialOpen: false,
      tutorialTrigger: null,
    }),
}));
