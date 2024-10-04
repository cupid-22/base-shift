// src/redux/reducer.js

import { UPLOAD_MENU } from './actionTypes';

const initialState = {
  menus: [],
};

export const menuReducer = (state = initialState, action) => {
  switch (action.type) {
    case UPLOAD_MENU:
      return {
        ...state,
        menus: [...state.menus, action.payload],
      };
    default:
      return state;
  }
};
