import {
    Divider, dividerClasses,
    IconButton,
    listClasses,
    ListItemIcon, listItemIconClasses,
    ListItemText,
    Menu,
    MenuItem as MuiMenuItem,
    paperClasses, styled
} from "@mui/material";
import {LogoutRounded, MoreVertRounded} from "@mui/icons-material";
import {useState} from "react";
import axios from "axios";
import {NavLink, useNavigate} from "react-router-dom";

const MenuItem = styled(MuiMenuItem)({
    margin: '2px 0',
});

export function UserMenu() {
    const navigate = useNavigate()
    const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null)
    const open = Boolean(anchorEl)

    const handleClick = (event: React.MouseEvent<HTMLElement>) => {
        setAnchorEl(event.currentTarget);
    }

    const handleClose = () => {
        setAnchorEl(null);
    }

    function logout() {
        axios.post("/api/auth/logout").then(() => {
            navigate('/login')
        }).catch(e => {
            console.warn(e)
        })
    }


    return <>
        <IconButton
            size={"small"}
            aria-label="Open menu"
            onClick={handleClick}
            sx={{ borderColor: 'transparent' }}
        >
            <MoreVertRounded />
        </IconButton>
        <Menu
            anchorEl={anchorEl}
            id="menu"
            open={open}
            onClose={handleClose}
            onClick={handleClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            sx={{
                [`& .${listClasses.root}`]: {
                    padding: '4px',
                },
                [`& .${paperClasses.root}`]: {
                    padding: 0,
                },
                [`& .${dividerClasses.root}`]: {
                    margin: '4px -4px',
                },
            }}
        >
            {
                // @ts-ignore
                <MenuItem to={'/profile'} component={NavLink} onClick={handleClose}>Profile</MenuItem>
            }
            <MenuItem onClick={handleClose}>Settings</MenuItem>
            <Divider />
            <MenuItem
                onClick={logout}
                sx={{
                    [`& .${listItemIconClasses.root}`]: {
                        ml: 'auto',
                        minWidth: 0,
                    },
                }}
            >
                <ListItemText>Logout</ListItemText>
                <ListItemIcon>
                    <LogoutRounded fontSize="small" />
                </ListItemIcon>
            </MenuItem>
        </Menu>
    </>
}
