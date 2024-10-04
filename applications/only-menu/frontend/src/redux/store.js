// src/redux/store.js

import { createStore } from 'redux';
import { menuReducer } from './reducer';

const store = createStore(menuReducer);

export default store;
