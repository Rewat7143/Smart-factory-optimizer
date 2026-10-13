with open('frontend/components/GlobalState.tsx', 'r') as f:
    content = f.read()

replacement = """
  useEffect(() => {
    const savedMode = localStorage.getItem('FEA_MODE') as Mode;
    if (savedMode) setMode(savedMode);
    
    // Intercept fetch to ALWAYS pass the global mode to the backend
    const originalFetch = window.fetch;
    window.fetch = async function() {
        let [resource, config] = arguments;
        if (typeof resource === 'string' && resource.includes('/api/')) {
            const currentMode = localStorage.getItem('FEA_MODE') || 'SIMULATION';
            const url = new URL(resource, window.location.origin);
            url.searchParams.set('mode', currentMode);
            resource = url.toString();
        }
        return originalFetch(resource, config);
    };
  }, []);

  const handleSetMode = (newMode: Mode) => {
    setMode(newMode);
    localStorage.setItem('FEA_MODE', newMode);
    window.location.reload(); // Reload to ensure all components fetch fresh data
  };
"""

import re
content = re.sub(r"  useEffect\(\(\) => \{.*?\}, \[\]\);\n\n  const handleSetMode = \(newMode: Mode\) => \{.*?  \};\n", replacement, content, flags=re.DOTALL)

with open('frontend/components/GlobalState.tsx', 'w') as f:
    f.write(content)
