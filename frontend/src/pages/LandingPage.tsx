import { Link } from 'react-router-dom';
import {
  BookOpen,
  BookMarked,
  Users,
  BarChart2,
  ShoppingBag,
  Scan,
  Bell,
  Shield,
  ArrowRight,
  CheckCircle2,
  Star,
  Zap,
  Globe,
} from 'lucide-react';
import { Button } from '../components/ui';

const features = [
  {
    icon: <BookOpen size={22} className="text-emerald-400" />,
    title: 'Catalog Management',
    desc: 'Add books manually or via OCR-assisted ISBN and cover scanning. Track copies and availability in real time.',
  },
  {
    icon: <Users size={22} className="text-emerald-400" />,
    title: 'Borrower Management',
    desc: 'Register borrowers with student ID scanning. Track membership, history, and active loans at a glance.',
  },
  {
    icon: <BookMarked size={22} className="text-emerald-400" />,
    title: 'Loans & Returns',
    desc: 'Issue and return books in seconds. Automatic overdue detection, fine calculation, and collection.',
  },
  {
    icon: <ShoppingBag size={22} className="text-emerald-400" />,
    title: 'Digital Bookstore',
    desc: 'Sell ebooks directly to readers. Secure in-platform reading with progress tracking and bookmarks.',
  },
  {
    icon: <Scan size={22} className="text-emerald-400" />,
    title: 'OCR Intelligence',
    desc: 'Scan ISBN barcodes, book covers, and student IDs. Powered by Gemini AI for instant metadata extraction.',
  },
  {
    icon: <BarChart2 size={22} className="text-emerald-400" />,
    title: 'Analytics & Reports',
    desc: 'Library-level and platform-wide dashboards. Borrowing trends, inventory growth, revenue analytics.',
  },
  {
    icon: <Bell size={22} className="text-emerald-400" />,
    title: 'Smart Notifications',
    desc: 'Automated overdue reminders, fine notices, purchase confirmations, and password resets via email.',
  },
  {
    icon: <Shield size={22} className="text-emerald-400" />,
    title: 'Enterprise Security',
    desc: 'Multi-tenant isolation with PostgreSQL RLS. JWT + Argon2 auth, RBAC, rate limiting, and audit logs.',
  },
];

const plans = [
  {
    name: 'Starter',
    price: '$29',
    period: '/month',
    description: 'Perfect for small school libraries',
    features: ['Up to 5,000 books', '500 active borrowers', 'Basic analytics', 'Email support'],
    cta: 'Start Free Trial',
    highlighted: false,
  },
  {
    name: 'Professional',
    price: '$89',
    period: '/month',
    description: 'For growing institutions',
    features: ['Unlimited books', '5,000 active borrowers', 'Digital bookstore', 'OCR scanning', 'Advanced analytics', 'Priority support'],
    cta: 'Start Free Trial',
    highlighted: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For universities and consortiums',
    features: ['Everything in Professional', 'Custom integrations', 'Dedicated support', 'SLA guarantee', 'On-premise option'],
    cta: 'Contact Sales',
    highlighted: false,
  },
];

const stats = [
  { value: '1,000+', label: 'Libraries Supported' },
  { value: '500K+', label: 'Books Catalogued' },
  { value: '2M+', label: 'Loans Processed' },
  { value: '99.9%', label: 'Platform Uptime' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-obsidian-950 text-white">
      {/* ── Navbar ────────────────────────────────────────────────────────── */}
      <nav className="fixed top-0 inset-x-0 z-50 border-b border-white/5 backdrop-blur-md bg-obsidian-950/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center">
              <BookOpen size={16} className="text-white" />
            </div>
            <span className="font-display font-bold text-xl tracking-tight">
              Soma<span className="text-emerald-400">Hub</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            {['Features', 'Pricing', 'About'].map((item) => (
              <a
                key={item}
                href={`#${item.toLowerCase()}`}
                className="text-sm text-obsidian-300 hover:text-white transition-colors"
              >
                {item}
              </a>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <Link to="/auth/login">
              <Button variant="ghost" size="sm" className="text-obsidian-300 hover:text-white hover:bg-white/10">
                Log in
              </Button>
            </Link>
            <Link to="/auth/signup/library">
              <Button variant="primary" size="sm">
                Start Free
              </Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* ── Hero ──────────────────────────────────────────────────────────── */}
      <section className="relative pt-32 pb-24 overflow-hidden">
        {/* Background mesh */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] rounded-full bg-emerald-600/10 blur-[120px]" />
          <div className="absolute top-1/3 right-1/4 w-[400px] h-[400px] rounded-full bg-sapphire-600/8 blur-[100px]" />
          {/* Grid lines */}
          <div
            className="absolute inset-0 opacity-[0.03]"
            style={{
              backgroundImage: 'linear-gradient(rgba(255,255,255,0.8) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.8) 1px, transparent 1px)',
              backgroundSize: '60px 60px',
            }}
          />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-medium mb-8 animate-fade-in">
            <Zap size={14} />
            Now with Gemini AI-powered OCR scanning
          </div>

          {/* Headline */}
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-display font-bold tracking-tight leading-[1.1] mb-6 animate-slide-up">
            Library Management
            <br />
            <span className="emerald-glow-text">Reimagined</span>
          </h1>

          {/* Sub-headline */}
          <p className="max-w-2xl mx-auto text-lg sm:text-xl text-obsidian-300 leading-relaxed mb-10 animate-slide-up">
            Manage books, borrowers, payments, digital reading, and analytics
            from one beautiful platform built for modern educational institutions.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-scale-in">
            <Link to="/auth/signup/library">
              <Button variant="primary" size="lg" rightIcon={<ArrowRight size={18} />} className="w-full sm:w-auto">
                Start Free — No credit card
              </Button>
            </Link>
            <Link to="/auth/signup/reader">
              <Button variant="outline" size="lg" className="w-full sm:w-auto border-white/20 text-white hover:border-emerald-400 hover:text-emerald-400">
                Browse Books
              </Button>
            </Link>
          </div>

          {/* Social proof */}
          <div className="flex items-center justify-center gap-6 mt-12 text-sm text-obsidian-400">
            <div className="flex items-center gap-1.5">
              <div className="flex -space-x-1">
                {['E', 'S', 'M', 'K'].map((l, i) => (
                  <div key={i} className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 border-2 border-obsidian-950 flex items-center justify-center text-white text-[9px] font-bold">
                    {l}
                  </div>
                ))}
              </div>
              <span>1,000+ libraries trust SomaHub</span>
            </div>
            <div className="hidden sm:flex items-center gap-1">
              {[1,2,3,4,5].map((s) => <Star key={s} size={13} className="fill-amber-400 text-amber-400" />)}
              <span className="ml-1">4.9/5</span>
            </div>
          </div>
        </div>

        {/* ── Dashboard Preview ── */}
        <div className="relative max-w-6xl mx-auto mt-20 px-4 sm:px-6">
          <div className="relative rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-obsidian-900">
            {/* Browser bar */}
            <div className="flex items-center gap-2 px-4 py-3 bg-obsidian-800/80 border-b border-white/5">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/70" />
                <div className="w-3 h-3 rounded-full bg-amber-500/70" />
                <div className="w-3 h-3 rounded-full bg-emerald-500/70" />
              </div>
              <div className="flex-1 mx-4 h-5 bg-obsidian-700 rounded-md flex items-center px-3">
                <span className="text-obsidian-500 text-xs">app.somahub.io/dashboard</span>
              </div>
            </div>

            {/* Dashboard mockup */}
            <div className="flex h-80">
              {/* Sidebar */}
              <div className="w-52 bg-obsidian-900 border-r border-white/5 p-3 space-y-1 hidden sm:block">
                <div className="flex items-center gap-2 px-3 py-2 mb-4">
                  <div className="w-6 h-6 rounded bg-emerald-600 flex items-center justify-center">
                    <BookOpen size={12} className="text-white" />
                  </div>
                  <span className="text-white text-sm font-bold">SomaHub</span>
                </div>
                {['Overview', 'Books', 'Borrowers', 'Loans', 'Fines', 'Analytics'].map((item, i) => (
                  <div
                    key={item}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs ${i === 0 ? 'bg-emerald-600 text-white' : 'text-obsidian-400'}`}
                  >
                    <div className="w-4 h-4 rounded bg-current opacity-40" />
                    {item}
                  </div>
                ))}
              </div>

              {/* Main content */}
              <div className="flex-1 p-5 overflow-hidden">
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                  {[
                    { label: 'Total Books', val: '12,847', color: 'text-emerald-400' },
                    { label: 'Active Loans', val: '342',    color: 'text-sapphire-400' },
                    { label: 'Overdue',      val: '28',     color: 'text-amber-400' },
                    { label: 'Fines Due',    val: 'KES 4.2K', color: 'text-red-400' },
                  ].map((stat) => (
                    <div key={stat.label} className="bg-obsidian-800/60 rounded-xl p-3 border border-white/5">
                      <p className="text-obsidian-400 text-xs mb-1">{stat.label}</p>
                      <p className={`text-xl font-bold font-display ${stat.color}`}>{stat.val}</p>
                    </div>
                  ))}
                </div>

                <div className="grid grid-cols-3 gap-3">
                  <div className="col-span-2 bg-obsidian-800/60 rounded-xl p-3 border border-white/5">
                    <p className="text-xs text-obsidian-400 mb-3">Borrowing Trends</p>
                    <div className="flex items-end gap-1 h-16">
                      {[40,65,50,80,70,90,75,95,60,85,70,100].map((h, i) => (
                        <div key={i} className="flex-1 bg-emerald-500/30 rounded-t hover:bg-emerald-500/50 transition-colors" style={{ height: `${h}%` }} />
                      ))}
                    </div>
                  </div>
                  <div className="bg-obsidian-800/60 rounded-xl p-3 border border-white/5">
                    <p className="text-xs text-obsidian-400 mb-3">Recent Activity</p>
                    <div className="space-y-2">
                      {['Book issued', 'Fine collected', 'New borrower', 'Book returned'].map((act) => (
                        <div key={act} className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                          <span className="text-xs text-obsidian-300">{act}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Glow effect */}
            <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-obsidian-950 to-transparent pointer-events-none" />
          </div>
        </div>
      </section>

      {/* ── Stats ─────────────────────────────────────────────────────────── */}
      <section className="border-y border-white/5 bg-white/[0.02]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14 grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat) => (
            <div key={stat.label} className="text-center">
              <p className="text-4xl font-display font-bold text-white mb-1">{stat.value}</p>
              <p className="text-sm text-obsidian-400">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ──────────────────────────────────────────────────────── */}
      <section id="features" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-display font-bold mb-4">
              Everything your library needs
            </h2>
            <p className="text-obsidian-400 text-lg max-w-2xl mx-auto">
              One platform replacing spreadsheets, paper logs, and disconnected tools.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="group relative p-6 rounded-2xl bg-white/[0.03] border border-white/5 hover:border-emerald-500/30 hover:bg-white/[0.06] transition-all duration-300"
              >
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 flex items-center justify-center mb-4 group-hover:bg-emerald-500/20 transition-colors">
                  {feature.icon}
                </div>
                <h3 className="font-display font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-obsidian-400 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Pricing ───────────────────────────────────────────────────────── */}
      <section id="pricing" className="py-24 bg-white/[0.01]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-display font-bold mb-4">Simple, transparent pricing</h2>
            <p className="text-obsidian-400 text-lg">Start free. Scale as you grow. No hidden fees.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative rounded-2xl p-8 border transition-all duration-300 ${
                  plan.highlighted
                    ? 'bg-emerald-600 border-emerald-500 shadow-emerald-glow scale-105'
                    : 'bg-white/[0.04] border-white/10 hover:border-white/20'
                }`}
              >
                {plan.highlighted && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-amber-400 text-obsidian-900 text-xs font-bold rounded-full">
                    MOST POPULAR
                  </div>
                )}
                <h3 className="font-display font-bold text-xl mb-1">{plan.name}</h3>
                <p className={`text-sm mb-4 ${plan.highlighted ? 'text-emerald-100' : 'text-obsidian-400'}`}>
                  {plan.description}
                </p>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-display font-bold">{plan.price}</span>
                  <span className={`text-sm ${plan.highlighted ? 'text-emerald-100' : 'text-obsidian-400'}`}>
                    {plan.period}
                  </span>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((f) => (
                    <li key={f} className="flex items-center gap-2.5 text-sm">
                      <CheckCircle2 size={16} className={plan.highlighted ? 'text-emerald-200' : 'text-emerald-500'} />
                      <span className={plan.highlighted ? 'text-emerald-50' : 'text-obsidian-300'}>{f}</span>
                    </li>
                  ))}
                </ul>
                <Link to="/auth/signup/library">
                  <Button
                    variant={plan.highlighted ? 'secondary' : 'outline'}
                    className={`w-full ${plan.highlighted ? 'bg-white text-emerald-700 hover:bg-emerald-50 border-0' : 'border-white/20 text-white hover:border-emerald-400'}`}
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ────────────────────────────────────────────────────── */}
      <section className="py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="relative rounded-3xl p-12 bg-gradient-to-br from-emerald-900/40 to-sapphire-900/20 border border-emerald-500/20 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-mesh opacity-30 pointer-events-none" />
            <Globe size={40} className="mx-auto text-emerald-400 mb-4" />
            <h2 className="text-4xl font-display font-bold mb-4">
              Ready to modernize your library?
            </h2>
            <p className="text-obsidian-300 text-lg mb-8 max-w-xl mx-auto">
              Join 1,000+ educational institutions already using SomaHub to simplify their library operations.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/auth/signup/library">
                <Button variant="primary" size="lg" rightIcon={<ArrowRight size={18} />}>
                  Start Free Trial
                </Button>
              </Link>
              <Link to="/auth/signup/reader">
                <Button variant="outline" size="lg" className="border-white/20 text-white hover:border-emerald-400">
                  Browse Bookstore
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────────────────────── */}
      <footer className="border-t border-white/5 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-emerald-600 flex items-center justify-center">
                <BookOpen size={14} className="text-white" />
              </div>
              <span className="font-display font-bold text-lg">
                Soma<span className="text-emerald-400">Hub</span>
              </span>
            </Link>
            <p className="text-sm text-obsidian-500">
              © {new Date().getFullYear()} SomaHub Enterprise. All rights reserved.
            </p>
            <div className="flex gap-6 text-sm text-obsidian-500">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
