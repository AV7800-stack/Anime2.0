import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import toast from 'react-hot-toast';
import { authAPI, dataAPI } from '../lib/api';
import { authUtils } from '../lib/auth';
import { 
  LayoutDashboard, 
  User, 
  LogOut, 
  Plus, 
  Search, 
  Filter,
  Heart,
  Eye,
  TrendingUp,
  BarChart3,
  Settings,
  Menu,
  X
} from 'lucide-react';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [stats, setStats] = useState({
    totalItems: 0,
    totalViews: 0,
    totalLikes: 0,
    recentActivity: 0
  });

  // Check authentication and load data
  useEffect(() => {
    if (!authUtils.isAuthenticated()) {
      router.push('/login');
      return;
    }

    loadUserData();
    loadData();
  }, [router]);

  const loadUserData = async () => {
    try {
      const response = await authAPI.getProfile();
      if (response.success) {
        setUser(response.data.user);
      }
    } catch (error) {
      console.error('Failed to load user data:', error);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const params = {
        page: 1,
        limit: 20,
        ...(searchTerm && { search: searchTerm }),
        ...(selectedCategory !== 'all' && { category: selectedCategory })
      };
      
      const response = await dataAPI.getAll(params);
      if (response.success) {
        setData(response.data.items);
        setStats({
          totalItems: response.data.pagination.total,
          totalViews: response.data.items.reduce((sum, item) => sum + (item.views || 0), 0),
          totalLikes: response.data.items.reduce((sum, item) => sum + (item.likes?.length || 0), 0),
          recentActivity: response.data.items.filter(item => 
            new Date(item.createdAt) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
          ).length
        });
      }
    } catch (error) {
      toast.error('Failed to load data');
      console.error('Load data error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      authUtils.logout();
      toast.success('Logged out successfully');
    } catch (error) {
      authUtils.logout(); // Force logout even if API call fails
    }
  };

  const handleLike = async (itemId) => {
    try {
      const response = await dataAPI.like(itemId);
      if (response.success) {
        // Update the item in the list
        setData(prevData => 
          prevData.map(item => 
            item._id === itemId 
              ? { ...item, likes: response.data.isLiked ? [...(item.likes || []), response.data.userId] : item.likes.filter(id => id !== response.data.userId) }
              : item
          )
        );
        toast.success(response.data.message);
      }
    } catch (error) {
      toast.error('Failed to update like');
    }
  };

  const filteredData = data.filter(item =>
    item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-700"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <h1 className="text-xl font-bold">Dashboard</h1>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-2 bg-gray-700 rounded-lg px-3 py-2">
              <Search className="w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="bg-transparent outline-none text-sm w-48"
              />
            </div>
            
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-400">
                Welcome, {user?.name || 'User'}
              </span>
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:static inset-y-0 left-0 z-50 w-64 bg-gray-800 border-r border-gray-700 transition-transform duration-300 ease-in-out`}>
          <div className="p-6">
            <nav className="space-y-6">
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Main</h3>
                <div className="space-y-2">
                  <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg bg-blue-600 text-white">
                    <LayoutDashboard className="w-4 h-4" />
                    <span>Dashboard</span>
                  </button>
                  <button 
                    onClick={() => router.push('/profile')}
                    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-700 text-gray-300"
                  >
                    <User className="w-4 h-4" />
                    <span>Profile</span>
                  </button>
                </div>
              </div>
              
              <div>
                <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">Actions</h3>
                <div className="space-y-2">
                  <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-700 text-gray-300">
                    <Plus className="w-4 h-4" />
                    <span>Create New</span>
                  </button>
                  <button className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-gray-700 text-gray-300">
                    <Settings className="w-4 h-4" />
                    <span>Settings</span>
                  </button>
                </div>
              </div>
              
              <div className="pt-6 border-t border-gray-700">
                <button
                  onClick={handleLogout}
                  className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-red-600 text-red-400 hover:text-white transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Logout</span>
                </button>
              </div>
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Items</p>
                  <p className="text-2xl font-bold text-white mt-1">{stats.totalItems}</p>
                </div>
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-blue-500" />
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Views</p>
                  <p className="text-2xl font-bold text-white mt-1">{stats.totalViews}</p>
                </div>
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
                  <Eye className="w-6 h-6 text-green-500" />
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Likes</p>
                  <p className="text-2xl font-bold text-white mt-1">{stats.totalLikes}</p>
                </div>
                <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
                  <Heart className="w-6 h-6 text-red-500" />
                </div>
              </div>
            </div>
            
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Recent Activity</p>
                  <p className="text-2xl font-bold text-white mt-1">{stats.recentActivity}</p>
                </div>
                <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
                  <TrendingUp className="w-6 h-6 text-purple-500" />
                </div>
              </div>
            </div>
          </div>

          {/* Data Grid */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold">Your Content</h2>
              <div className="flex items-center space-x-3">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="all">All Categories</option>
                  <option value="anime">Anime</option>
                  <option value="manga">Manga</option>
                  <option value="character">Character</option>
                  <option value="story">Story</option>
                  <option value="video">Video</option>
                </select>
                <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg">
                  <Plus className="w-4 h-4" />
                  <span>Add New</span>
                </button>
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredData.map((item) => (
                  <div key={item._id} className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700 hover:border-gray-600 transition-colors">
                    {item.imageUrl && (
                      <div className="h-48 bg-gray-700 relative">
                        <img 
                          src={item.imageUrl} 
                          alt={item.title}
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute top-2 right-2 bg-black/50 px-2 py-1 rounded text-xs">
                          {item.category}
                        </div>
                      </div>
                    )}
                    
                    <div className="p-4">
                      <h3 className="font-semibold text-white mb-2 line-clamp-1">{item.title}</h3>
                      <p className="text-gray-400 text-sm mb-4 line-clamp-2">{item.description}</p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4 text-gray-400 text-sm">
                          <span className="flex items-center space-x-1">
                            <Eye className="w-4 h-4" />
                            {item.views || 0}
                          </span>
                          <span className="flex items-center space-x-1">
                            <Heart className="w-4 h-4" />
                            {item.likes?.length || 0}
                          </span>
                        </div>
                        
                        <button
                          onClick={() => handleLike(item._id)}
                          className="text-red-400 hover:text-red-300"
                        >
                          <Heart className="w-5 h-5" fill={item.likes?.includes(user?._id) ? 'currentColor' : 'none'} />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!loading && filteredData.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>No content found</p>
                  <p className="text-sm mt-2">Try adjusting your search or filters</p>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}
