'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import {
    Users,
    TrendingUp,
    Activity,
    Search,
    ShieldAlert,
    DollarSign,
    MoreHorizontal
} from 'lucide-react'
import { apiFetch } from '@/lib/api-client'
import { toast } from 'sonner'
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useUser } from '@/lib/user-context'
import { useRouter } from 'next/navigation'

// --- Types ---

interface AdminStats {
    total_users: number
    users_24h: number
    active_plans: number
    hidden_signals: number
    total_signals: number
    signals_24h: number
    system_status: string
    mrr: number
    last_updated: string
}

interface AdminUser {
    id: number
    email: string
    role: string
    plan: string
    created_at: string
}

interface UserListResponse {
    items: AdminUser[]
    total: number
    page: number
    size: number
}

// --- Component ---

export default function AdminPage() {
    const { user } = useUser()
    const router = useRouter()

    const [stats, setStats] = useState<AdminStats | null>(null)
    const [users, setUsers] = useState<AdminUser[]>([])
    const [searchQuery, setSearchQuery] = useState('')
    const [isLoading, setIsLoading] = useState(true)

    // Auth Check (Client-side protection)
    // Backend also checks, but this prevents flashing
    useEffect(() => {
        if (user && user.plan !== 'OWNER' && user.email !== 'tsmluky@gmail.com') {
            router.push('/dashboard')
        }
    }, [user, router])

    const loadData = async () => {
        setIsLoading(true)
        try {
            const [statsData, usersData] = await Promise.all([
                apiFetch<AdminStats>('/admin/stats'),
                apiFetch<UserListResponse>(`/admin/users?q=${searchQuery}`)
            ])
            setStats(statsData)
            setUsers(usersData.items)
        } catch (e) {
            console.error("Admin load error", e)
            toast.error("Failed to load admin data")
        } finally {
            setIsLoading(false)
        }
    }

    useEffect(() => {
        // Only load if likely authorized
        loadData()
    }, []) // Initial load

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        loadData()
    }

    const handleUpdatePlan = async (userId: number, newPlan: string) => {
        try {
            await apiFetch(`/admin/users/${userId}/plan`, {
                method: 'PATCH',
                body: JSON.stringify({ plan: newPlan })
            })
            toast.success(`User upgraded to ${newPlan}`)
            loadData() // Refresh list
        } catch (e) {
            toast.error("Failed to update plan")
        }
    }

    if (!stats) return <div className="p-8 text-center animate-pulse">Loading Admin Console...</div>

    return (
        <div className="space-y-8 p-1">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight mb-1 flex items-center gap-2">
                        <ShieldAlert className="h-8 w-8 text-primary" />
                        Admin Control
                    </h1>
                    <p className="text-muted-foreground">System Management & Audits</p>
                </div>
                <div className="flex items-center gap-2">
                    <Badge variant="outline" className="bg-emerald-500/10 text-emerald-500 border-emerald-500/20 px-3 py-1">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse" />
                        {stats.system_status}
                    </Badge>
                </div>
            </div>

            {/* KPI Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_users}</div>
                        <p className="text-xs text-muted-foreground">+{stats.users_24h} in last 24h</p>
                    </CardContent>
                </Card>

                <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Active Subscriptions</CardTitle>
                        <TrendingUp className="h-4 w-4 text-emerald-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-emerald-500">{stats.active_plans}</div>
                        <p className="text-xs text-muted-foreground">Pro & Owner accounts</p>
                    </CardContent>
                </Card>

                <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Signals</CardTitle>
                        <Activity className="h-4 w-4 text-primary" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_signals}</div>
                        <p className="text-xs text-muted-foreground">+{stats.signals_24h} generated 24h</p>
                    </CardContent>
                </Card>

                <Card className="bg-card/50 backdrop-blur-sm border-border/50">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Est. Monthly Revenue</CardTitle>
                        <DollarSign className="h-4 w-4 text-amber-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-amber-500">${stats.mrr.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">Based on active plans</p>
                    </CardContent>
                </Card>
            </div>

            {/* User Management */}
            <div className="space-y-4">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                        {/* Tabs / Filter could go here */}
                        <h2 className="text-lg font-semibold">User Management</h2>
                    </div>
                    <form onSubmit={handleSearch} className="flex w-full max-w-sm items-center space-x-2">
                        <div className="relative flex-1">
                            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                            <Input
                                type="search"
                                placeholder="Search by email..."
                                className="pl-9 bg-background/50"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                        <Button type="submit" size="sm">Search</Button>
                    </form>
                </div>

                <div className="rounded-md border border-border/50 bg-card/30 overflow-hidden">
                    <Table>
                        <TableHeader>
                            <TableRow className="bg-muted/50 hover:bg-muted/50">
                                <TableHead className="w-[80px]">ID</TableHead>
                                <TableHead>Email</TableHead>
                                <TableHead>Role</TableHead>
                                <TableHead>Plan</TableHead>
                                <TableHead>Joined</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {users.map((u) => (
                                <TableRow key={u.id} className="hover:bg-muted/5">
                                    <TableCell className="font-mono text-xs text-muted-foreground">#{u.id}</TableCell>
                                    <TableCell className="font-medium">{u.email}</TableCell>
                                    <TableCell>
                                        <Badge variant="outline" className="opacity-80 scale-90 origin-left">{u.role}</Badge>
                                    </TableCell>
                                    <TableCell>
                                        <Badge
                                            className={
                                                u.plan === 'PRO' ? 'bg-primary/20 text-primary hover:bg-primary/30' :
                                                    u.plan === 'OWNER' ? 'bg-amber-500/20 text-amber-500 hover:bg-amber-500/30' :
                                                        'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                                            }
                                        >
                                            {u.plan}
                                        </Badge>
                                    </TableCell>
                                    <TableCell className="text-sm text-muted-foreground">
                                        {new Date(u.created_at).toLocaleDateString()}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button variant="ghost" className="h-8 w-8 p-0">
                                                    <span className="sr-only">Open menu</span>
                                                    <MoreHorizontal className="h-4 w-4" />
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuLabel>Actions</DropdownMenuLabel>
                                                <DropdownMenuSeparator />
                                                <DropdownMenuItem onClick={() => handleUpdatePlan(u.id, 'PRO')} className="text-primary cursor-pointer">
                                                    Upgrade to PRO
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onClick={() => handleUpdatePlan(u.id, 'TRADER')} className="cursor-pointer">
                                                    Set to TRADER (Lite)
                                                </DropdownMenuItem>
                                                <DropdownMenuSeparator />
                                                <DropdownMenuItem onClick={() => handleUpdatePlan(u.id, 'FREE')} className="text-muted-foreground cursor-pointer">
                                                    Downgrade to FREE
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}
                            {users.length === 0 && !isLoading && (
                                <TableRow>
                                    <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                                        No users found.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>
        </div>
    )
}
