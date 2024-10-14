const backendBase = '$VITE_API_BASE'

export const getBackendBase = () => getVar(backendBase)

function getVar(key: string) {
    if (key.startsWith('$VITE_'))
    {
        return key.substring(1) in import.meta.env ? import.meta.env[key.substring(1)] : '';
    }
    return key;
}
