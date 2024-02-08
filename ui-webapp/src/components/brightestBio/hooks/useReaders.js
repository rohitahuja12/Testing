import { useState, useCallback, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getDefaultReader } from '../../../actions/readerActions';
import { readerSelector } from '../../../features/reader/readerSlice';
import { useAuth } from './useAuth';
import { setToken } from '../../../features/system/systemSlice';

export const useReaders = () => {
  const dispatch = useDispatch();
  const readers = useSelector(readerSelector)?.readers;
  const { getAccessToken } = useAuth();

  useEffect(() => {
    try {
      const getAccessTokenSilently = async () => {
        const token = await getAccessToken();
        dispatch(setToken(token));
        if (readers?.length === 0 || !readers) {
          dispatch(getDefaultReader(token));
        }
      };
      getAccessTokenSilently();
    } catch (error) {
      if (window.location.pathname.includes("/login")) return;
      window.location.href = window.location.origin + '/login';
    }
  }, [dispatch, readers]);

  return { readers };
}
