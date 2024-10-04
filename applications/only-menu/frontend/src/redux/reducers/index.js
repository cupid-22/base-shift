import { combineReducers } from 'redux';
import userReducer from './userReducer';
import menuReducer from './menuReducer';

export default combineReducers({
  user: userReducer,
  menu: menuReducer,
});
