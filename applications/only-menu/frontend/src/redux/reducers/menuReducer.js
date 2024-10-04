// src/redux/reducers/menuReducer.js

const initialState = {
  menus: [],
};

const menuReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'UPLOAD_MENU':
      return {
        ...state,
        menus: [...state.menus, action.payload],
      };
    default:
      return state;
  }
};

export default menuReducer;
