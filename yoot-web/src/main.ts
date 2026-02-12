import { GameUI } from './ui/gameUI';

const fast = new URLSearchParams(window.location.search).has('fast');
const gameUI = new GameUI(fast);
gameUI.init();
