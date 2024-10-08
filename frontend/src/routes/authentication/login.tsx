import {useState} from "react";
import axios from "axios";
import {useLocation, useNavigate} from "react-router-dom";
import {FullpageFormContainer} from "../../components/FullpageFormContainer.tsx";
import {
    Button,
    Box,
    Typography,
    FormControl,
    FormLabel,
    TextField,
    Divider
} from "@mui/material";
import {getBackendBase} from "../../config.ts";

export default function Login() {

    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState<boolean>(false)

    let {state} = useLocation()
    let navigate = useNavigate()

    const redirectTarget = (state != null && state.loginRedirect && state.loginRedirect !== "/login") ?
        state.loginRedirect : '/'

    function onSubmit(e: any) {
        e.preventDefault()
        setLoading(true)

        axios.post("/api/auth/login", {
            username: username,
            password: password
        }).then(e => {
            console.log(e)
            console.log("state", state)
            setLoading(false)
            navigate(redirectTarget)
        }).catch(e => {
            console.warn(e)
            setLoading(false)
        })
    }

    function satosaRedirect() {
        window.location.href = getBackendBase() + '/oidc/login?next=' + encodeURIComponent(redirectTarget)
    }

    return <FullpageFormContainer>
        <Typography
            component="h1"
            variant="h4"
            sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.15rem)' }}
        >
            Sign in
        </Typography>
        <Box
            component={"form"}
            onSubmit={onSubmit}
            noValidate
            sx={{
                display: 'flex',
                flexDirection: 'column',
                width: '100%',
                gap: 2
            }}
        >
            <FormControl>
                <FormLabel htmlFor="email">Email</FormLabel>
                <TextField
                    // error={emailError}
                    // helperText={emailErrorMessage}
                    id="email"
                    type="email"
                    name="email"
                    placeholder="your@email.com"
                    autoComplete="email"
                    autoFocus
                    required
                    fullWidth
                    variant="outlined"
                    // color={emailError ? 'error' : 'primary'}
                    onChange={e => setUsername(e.target.value)}
                    value={username}
                    sx={{ ariaLabel: 'email' }}
                />
            </FormControl>
            <FormControl>
                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <FormLabel htmlFor="password">Password</FormLabel>
                </Box>
                <TextField
                    // error={passwordError}
                    // helperText={passwordErrorMessage}
                    name="password"
                    placeholder="••••••"
                    type="password"
                    id="password"
                    autoComplete="current-password"
                    required
                    fullWidth
                    variant="outlined"
                    onChange={e => setPassword(e.target.value)}
                    value={password}
                    // color={passwordError ? 'error' : 'primary'}
                />
            </FormControl>
            <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
            >
                Sign in
            </Button>
        </Box>
        <Divider>or</Divider>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Button
                type="submit"
                fullWidth
                variant="outlined"
                onClick={satosaRedirect}
                disabled={loading}
            >
                Use Satosa
            </Button>
        </Box>
    </FullpageFormContainer>
}
