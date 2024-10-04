// src/redux/reducers/userReducer.js

const initialState = {
  username: null,
};

const userReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        username: action.payload.username,
      };
    default:
      return state;
  }
};

export default userReducer;
