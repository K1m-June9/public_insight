import AdminPage from "@/components/AdminPage"
import Header from "@/components/Header"
import Footer from "@/components/Footer"

export default function AdminPageRoute() {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow">
        <AdminPage />
      </main>
      <Footer />
    </div>
  )
}

