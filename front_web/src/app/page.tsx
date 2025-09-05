import Header from "@/components/header"
import Footer from "@/components/footer"
import MainContent from "@/components/main-content"
import { ScrollToTopButton } from "@/components/ScrollToTop"

export default function Home() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-grow">
        <MainContent />
      </main>
      <Footer />
      <ScrollToTopButton />
    </div>
  )
}
