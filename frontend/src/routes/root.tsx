import './root.scss'
import {NavLink, Outlet, useLoaderData, useNavigate, useLocation} from "react-router-dom";
import axios from 'axios'
import {forwardRef, LegacyRef, ReactElement, useEffect, useState} from "react";
import {
    Box,
    Divider,
    List,
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    ListSubheader,
    MenuItem,
    Stack,
    styled,
    Typography
} from "@mui/material";

import MuiDrawer, { drawerClasses } from '@mui/material/Drawer';
import Select, { SelectChangeEvent, selectClasses } from '@mui/material/Select';

import {AppsRounded, CategoryRounded, KeyRounded, SendRounded} from "@mui/icons-material";
import {UserMenu} from "../components/UserMenu.tsx";

export interface IApp {
    name: string
    mnemonic: string
    current_role: string
}

export interface IRoute {
    icon: ReactElement,
    name: string,
    location: string
}

export interface IUserData {
    username: string,
    nickname: string,
    role: string,
    profileComplete: boolean,
    isOidc: boolean,
}

const drawerWidth = 240

const Drawer = styled(MuiDrawer)({
    width: drawerWidth,
    flexShrink: 0,
    boxSizing: 'border-box',
    mt: 10,
    [`& .${drawerClasses.paper}`]: {
        width: drawerWidth,
        boxSizing: 'border-box',
    },
});

const CustomNavLink = forwardRef((props, ref) => {
    const propsWithClassname = props as { className: string, to: string }
    return <NavLink
        ref={ref as LegacyRef<HTMLAnchorElement>}
        {...propsWithClassname}
        className={({isActive}) => (isActive ? propsWithClassname.className + ' Mui-selected' : propsWithClassname.className)}
        end
    />
});

export async function loader() {


    let authFailed = false
    const authResponse = await axios.get('/api/auth/me').catch(() => {
        authFailed = true
    })

    let userData = {}

    if (authResponse !== undefined) {
        console.log(authResponse)
        authFailed = authResponse.status !== 200
        userData = authResponse.data
    }

    const appsResult = await axios.get('/api/apps/list')
    const apps = appsResult.data.applications;

    return {authSuccessful: !authFailed, userDataRaw: userData, apps: apps}
}

interface ILoaderResponse {
    authSuccessful: boolean,
    userDataRaw: object,
    apps: IApp[],
}

export function Root() {

    let {authSuccessful, userDataRaw, apps} = useLoaderData() as ILoaderResponse
    const navigate = useNavigate();
    const location = useLocation()

    let appRoutes: IRoute[] = [
        {
            icon: <AppsRounded />,
            name: "Overview",
            location: ''
        },
    ]

    let secondaryRoutes: IRoute[] = [
        {
            icon: <KeyRounded />,
            name: "Manage API keys",
            location: "/keys"
        },
    ]

    useEffect(() => {
        if (!authSuccessful || Object.keys(userDataRaw).length === 0) {
            navigate('/login', {state: { loginRedirect: location.pathname }})
            return
        }

        let data = userDataRaw as IUserData

        if (!data.profileComplete) {
            navigate('/complete-profile', {state: { loginRedirect: location.pathname }})
            return
        }
    }, [authSuccessful, userDataRaw])

    const userData = userDataRaw as IUserData

    const [selectedApp, setSelectedApp] = useState(apps[0])

    if (selectedApp.current_role == 'operator') {
        appRoutes.push({
            icon: <SendRounded />,
            name: "Invitations",
            location: '/invitations'
        })
        appRoutes.push({
            icon: <CategoryRounded />,
            name: "Items",
            location: '/items'
        })
    }

    function handleAppSelect(e: SelectChangeEvent) {
        apps.forEach((app) => {
            if (app.mnemonic === e.target.value) {
                setSelectedApp(app)
                navigate('/apps/' + app.mnemonic)
            }
        })
    }

    return (
        <>
            <div id={'background'} ></div>
            <Box sx={{display: 'flex'}}>
                <Drawer
                    variant="permanent"
                    sx={{
                        display: { xs: 'none', md: 'block' },
                        [`& .${drawerClasses.paper}`]: {
                            backgroundColor: 'background.paper',
                        },
                    }}
                >
                    <Box
                        sx={{
                            display: 'flex',
                            mt: 'calc(var(--template-frame-height, 0px) + 4px)',
                            p: 1.5,
                        }}
                    >
                        <Select
                            labelId="company-select"
                            id="company-simple-select"
                            value={selectedApp == undefined ? undefined : selectedApp.mnemonic}
                            onChange={handleAppSelect}
                            displayEmpty
                            inputProps={{ 'aria-label': 'Select company' }}
                            fullWidth
                            sx={{
                                maxHeight: 56,
                                width: 215,
                                '&.MuiList-root': {
                                    p: '8px',
                                },
                                [`& .${selectClasses.select}`]: {
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '2px',
                                    pl: 1,
                                },
                            }}
                        >
                            <ListSubheader sx={{pt: 0}}>Applications</ListSubheader>
                            {apps.map((app, i) => {
                                return <MenuItem key={i} value={app.mnemonic}>
                                    <ListItemText primary={app.name} secondary={app.current_role} />
                                </MenuItem>
                            })}
                        </Select>
                    </Box>
                    <Divider />
                    <Stack sx={{ flexGrow: 1, p: 1, justifyContent: 'space-between' }}>
                        {selectedApp != undefined ? (
                            <List dense>
                                {appRoutes.map((item, index) => {
                                    return <ListItem key={index} disablePadding sx={{display: 'block'}}>
                                        {
                                            // @ts-ignore
                                            <ListItemButton to={"/apps/" + selectedApp.mnemonic + item.location}
                                                            component={CustomNavLink}>
                                                <ListItemIcon>{item.icon}</ListItemIcon>
                                                <ListItemText primary={item.name}/>
                                            </ListItemButton>
                                        }
                                    </ListItem>
                                })}
                            </List>
                        ) : ''}

                        <List dense>
                            {secondaryRoutes.map((item, index) => (
                                <ListItem key={index} disablePadding sx={{ display: 'block' }}>
                                    {
                                        // @ts-ignore
                                        <ListItemButton to={item.location} component={CustomNavLink}>
                                            <ListItemIcon>{item.icon}</ListItemIcon>
                                            <ListItemText primary={item.name} />
                                        </ListItemButton>
                                    }
                                </ListItem>
                            ))}
                        </List>
                    </Stack>

                    <Stack
                        direction="row"
                        sx={{
                            p: 2,
                            gap: 1,
                            alignItems: 'center',
                            borderTop: '1px solid',
                            borderColor: 'divider',
                        }}
                    >
                        {/*<Avatar*/}
                        {/*    sizes="small"*/}
                        {/*    alt={userData.nickname}*/}
                        {/*    src="/static/images/avatar/7.jpg"*/}
                        {/*    sx={{ width: 36, height: 36 }}*/}
                        {/*/>*/}
                        <Box sx={{ mr: 'auto' }}>
                            <Typography variant="body2" sx={{ fontWeight: 500, lineHeight: '16px' }}>
                                {userData.nickname}
                            </Typography>
                            <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                                {userData.username}
                            </Typography>
                        </Box>
                        <UserMenu />
                    </Stack>
                </Drawer>

                <Box
                    component="main"
                    sx={(_theme) => ({
                        flexGrow: 1,
                        overflow: 'auto',
                    })}
                >
                    <Stack
                        spacing={2}
                        sx={{
                            alignItems: 'center',
                            mx: 3,
                            pb: 10,
                            mt: { xs: 8, md: 0 },
                        }}
                    >
                        <Outlet />
                    </Stack>
                </Box>
            </Box>
        </>
    )
}
