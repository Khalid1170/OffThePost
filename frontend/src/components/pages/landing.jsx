import "../styles/Landing.css";
import { ArrowDown } from "lucide-react";

function Landing() {
  return (
    <div className="page relative min-h-screen">
      <div className="container flex items-center justify-between">
        {/* Left section */}
        <div className="otp max-w-lg">
          <h1>
            Welcome to <span className="highlight">Off The Post -</span> Track
            Every Kick, Goal, and Win.
          </h1>
          <p>
            Play with friends, compare stats, and relive every match with your
            group.
          </p>

          <div className="buttons mt-4">
            <a href="/Authpage" className="btn primary">
              Join
            </a>
          </div>
        </div>

        {/* Right section for image */}
        <div className="pic">
          <img
            src="/image.png"
            alt="Football tracking illustration"
            className="w-full max-w-md"
          />
        </div>
      </div>

      {/* Scroll indicator */}
       <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex flex-col items-center animate-bounce">
        <span className="text-sm text-muted-foreground mb-2">Scroll to see more features</span>
        <ArrowDown className="h-5 w-5 text-primary" />
      </div> 

  
    </div>

    
  );
}

export default Landing;
