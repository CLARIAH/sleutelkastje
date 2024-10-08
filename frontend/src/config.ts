const backendBase = '$REACT_APP_API_BASE'

export const getBackendBase = () => getVar(backendBase)

function getVar(key: string) {
    if (key.startsWith('$REACT_APP_'))
        { // @ts-ignore
            return process.env[key.substring(1)];
        }
    return key;
}
