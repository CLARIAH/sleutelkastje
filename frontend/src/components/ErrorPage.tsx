import {Link, useLocation, useNavigate, useRouteError} from "react-router-dom";
import {useEffect} from "react";

interface IError {
    statusText: string,
    message: string,
    response: Response
}

export default function ErrorPage() {
    const error = useRouteError() as IError;

    const navigate = useNavigate();
    let location = useLocation()

    useEffect(() => {
        if (error.response == undefined) {
            return
        }

        if (error.response.status == 401) {
            const path = location.pathname
            console.log("Redirecting to login. Will set loginRedirect to ", path)
            navigate('/login', {state: {
                    loginRedirect: path
                }
            })
        }
    }, [error])

    return (
        <div className="row justify-content-center">
            <div className="col-md-12 text-center">
                <span className="display-1 d-block">{error.statusText}</span>
                <div className="mb-4 lead">{error.message}</div>
                <Link to="/" className="btn btn-link">Back to Home</Link>
            </div>
        </div>
    )
}
