import {Outlet} from "react-router-dom";
import {Box, Typography} from "@mui/material";

export function Applications() {

    return <>
        <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
            <Typography component="h2" variant="h2" sx={{mb: 2}}>
                Applications
            </Typography>
            {/*<Box sx={{borderBottom: 1, borderColor: 'divider'}}>*/}
            {/*    <Tabs>*/}
            {/*        {apps.map(app => {*/}
            {/*            return <Tab component={NavLink} to={'/apps/' + app.name} label={app.name} />*/}
            {/*        })}*/}
            {/*    </Tabs>*/}
            {/*</Box>*/}
            <Outlet />
        </Box>
        {/*<h1>Applications</h1>*/}
        {/*<hr />*/}
        {/*<div className={'row'}>*/}
        {/*    <div className={'col-md-2'}>*/}
        {/*        <div className={'list-group'}>*/}
        {/*            {apps.map((app) => {*/}
        {/*                return <NavLink key={app.name} to={'/apps/' + app.name} className={'list-group-item'}>{app.name}</NavLink>*/}
        {/*            })}*/}
        {/*        </div>*/}
        {/*    </div>*/}
        {/*    <div className={'col-md-10'}>*/}
        {/*        <Outlet />*/}
        {/*    </div>*/}
        {/*</div>*/}
    </>
}
