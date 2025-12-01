import { NavLink } from "react-router"
import {
  SignedIn,
  SignedOut,
  SignInButton,
  SignUpButton,
  UserButton,
} from "@clerk/clerk-react"

interface NavigationItem {
  name: string;
  href: string;
}

const navigation: NavigationItem[] = [
  { name: 'Host', href: 'host' },
  { name: 'Client', href: 'client' },
]

export default function NavBar() {
  return (
    <div className="sticky top-0 z-50 bg-gray-300 shadow-lg">
      <nav className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center">
          <div className="flex justify-center flex-1 space-x-8">
            {navigation.map((item) => (
              <NavLink
                to={item.href}
                key={item.name}
                end
                className={({ isActive }) =>
                  `m-2 px-6 py-2 text-lg font-medium transition-colors duration-200 rounded-full ${
                    isActive
                      ? 'text-white bg-gray-700'
                      : 'text-black border-transparent hover:text-white hover:bg-gray-700'
                  }`
                }
              >
                {item.name}
              </NavLink>
            ))}
          </div>
          <div className="flex items-center space-x-4">
            <SignedOut>
              <SignInButton mode="modal">
                <button className="px-4 py-2 text-sm font-medium text-black rounded-full hover:bg-gray-700 hover:text-white transition-colors duration-200">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="px-4 py-2 text-sm font-medium text-white bg-gray-700 rounded-full hover:bg-gray-800 transition-colors duration-200">
                  Sign Up
                </button>
              </SignUpButton>
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </div>
        </div>
      </nav>
    </div>
  )
}