import { NavLink } from "react-router"

const navigation = [
  { name: 'Host', href: 'host' },
  { name: 'Client', href: 'client' },
]

export default function NavBar() {
  return (
    <div className="bg-gray-300 shadow-lg">
      <nav className="max-w-6xl mx-auto px-4">
        <div className="flex justify-center space-x-8">
          {navigation.map((item) => (
            <NavLink 
              to={item.href} 
              key={item.name} 
              end
              className={({ isActive }) =>
                `m-2 px-6 py-2 text-lg font-medium transition-colors duration-200 rounded-md  ${
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
      </nav>
    </div>
  )
}