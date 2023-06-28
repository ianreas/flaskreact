import '../styles/globals.css'
import '../styles/Navbar.css'

import {Link} from 'react-router-dom'


export default function Navbar() {
    
    

    return (
        <nav  className='navbar'>
            <Link to='/' className='site-title'>BUIDLING ALPHA</Link>
            <ul>
                <CustomLink to='/contact'>Contact</CustomLink>
                <CustomLink to='/about'>About</CustomLink>
                <CustomLink to='/spy'>Stock Price and Etc</CustomLink>
                <CustomLink to='/newspy'>tradingviewchart</CustomLink>
            </ul>
        </nav>
    )
    }


function CustomLink({to, children, ...props}){
    const path = window.location.pathname

    return (
        <li className={path === to ? 'active' : ""}>
            <Link to={to} {...props}>
                {children}
            </Link>
        </li>
    )
}


/*
<li>
                    <button className="signin">
                        SIGN IN
                    </button>
                </li>
                <li>
                    <button className='btn-logo'>BUILD ALPHA</button>
                </li>
                <li>
                    <img src={"/logo.png"}/>
                </li>
*/