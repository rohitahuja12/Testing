import { useCallback, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux"
import { getDefaultFeatureFlags, isFeatureFlagEnabled } from "../../../actions/featureFlagActions";


export const useFeatureFlags = () => {
    const dispatch = useDispatch();
    const featureFlags = useSelector(state => state.system.featureFlags);
    const featureFlagExpiration = useSelector(state => state.system.featureFlagExpiration);

    useEffect(() => {
        if (Date.now() > featureFlagExpiration || !featureFlags || featureFlags.length === 0) {
            dispatch(getDefaultFeatureFlags());
        }
    }, [dispatch]);

    const checkFeatureFlag = useCallback(
        /**
         * 
         * @param {string} featureFlag 
         * @returns boolean
         */
        (featureFlag) => isFeatureFlagEnabled(featureFlag, featureFlags) || false,
        [featureFlags]
    );


    return { featureFlags, checkFeatureFlag };
}
