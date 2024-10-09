const backendBase = '$VITE_API_BASE'

export const getBackendBase = () => getVar(backendBase)

function getVar(key: string) {
    if (key.startsWith('$VITE_'))
        {
            return import.meta.env[key.substring(1)];
        }
    return key;
}
