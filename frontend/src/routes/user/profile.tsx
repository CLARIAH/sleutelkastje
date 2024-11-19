import {Box, Typography} from "@mui/material";

export function Profile() {
    return <>
        <Box sx={{ width: '100%', maxWidth: { sm: '100%', md: '1700px' } }}>
            <Typography component="h2" variant="h2" sx={{mb: 2}}>
                Profile
            </Typography>
        </Box>
    </>
}
