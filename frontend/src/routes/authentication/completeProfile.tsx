import {useState} from "react";
import axios from "axios";
import {useLoaderData, useLocation, useNavigate} from "react-router-dom";
import {IUserData} from "../root.tsx";
import {
    Box,
    Button,
    FormControl,
    FormLabel,
    TextField,
    Typography
} from "@mui/material";
import {FullpageFormContainer} from "../../components/FullpageFormContainer.tsx";

export async function completeProfileLoader() {
    const authResponse = await axios.get('/api/auth/me')

    const user: IUserData = authResponse.data

    return {user}
}

export function CompleteProfile() {
    const {user} = useLoaderData() as {user: IUserData};
    const [nickname, setNickname] = useState(user.nickname);
    const [loading, setLoading] = useState<boolean>(false)
    const navigate = useNavigate();
    let {state} = useLocation()

    const redirectTarget = (state != null && state.loginRedirect && state.loginRedirect !== "/login") ?
        state.loginRedirect : '/'

    function onSubmit(e: any) {
        e.preventDefault()
        setLoading(true)

        axios.post("/api/auth/complete-profile", {
            nickname: nickname
        }).then(e => {
            console.log(e)
            setLoading(false)
            navigate(redirectTarget)
        }).catch(e => {
            console.warn(e)
            setLoading(false)
        })
    }

    function logout() {
        axios.post("/api/auth/logout").then(() => {
            navigate('/login')
        }).catch(e => {
            console.warn(e)
        })
    }

    return <FullpageFormContainer>
        <Typography
            component="h1"
            variant="h4"
            sx={{ width: '100%', fontSize: 'clamp(2rem, 10vw, 2.15rem)' }}
        >
            Complete Profile
        </Typography>
        <Typography>
            Thank you for signing up for the Sleutelkastje! Before you can continue, please complete
            your profile by filling out this form.
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
                <FormLabel htmlFor="email">Username</FormLabel>
                <TextField
                    id="email"
                    type="email"
                    name="email"
                    placeholder="your@email.com"
                    autoComplete="email"
                    disabled
                    fullWidth
                    variant="outlined"
                    value={user.username}
                    sx={{ ariaLabel: 'email' }}
                />
            </FormControl>
            <FormControl>
                <FormLabel htmlFor="email">Nickname</FormLabel>
                <TextField
                    id="email"
                    type="email"
                    name="email"
                    placeholder="your@email.com"
                    autoComplete="email"
                    autoFocus
                    required
                    fullWidth
                    variant="outlined"
                    onChange={e => setNickname(e.target.value)}
                    value={nickname}
                    sx={{ ariaLabel: 'email' }}
                />
            </FormControl>
            <Button
                type="submit"
                fullWidth
                variant="contained"
                disabled={loading}
            >
                Save
            </Button>
            <Button
                fullWidth
                onClick={logout}
                variant="outlined"
                disabled={loading}
            >
                Complete later (log out)
            </Button>
        </Box>
    </FullpageFormContainer>
}
