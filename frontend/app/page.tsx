export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4">VehicleIQ</h1>
        <p className="text-xl text-muted-foreground mb-8">
          AI-Powered Vehicle Assessment Platform
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-12">
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Fraud Detection</h2>
            <p className="text-muted-foreground">
              9 fraud signals with explainable AI and confidence scoring
            </p>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Price Prediction</h2>
            <p className="text-muted-foreground">
              4-layer model with RAG-based comparables and persona-specific values
            </p>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Image Intelligence</h2>
            <p className="text-muted-foreground">
              OCR extraction and damage detection with quality gates
            </p>
          </div>
          
          <div className="p-6 border rounded-lg">
            <h2 className="text-2xl font-semibold mb-2">Health Scoring</h2>
            <p className="text-muted-foreground">
              Persona-specific weighted scoring with explainable components
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
