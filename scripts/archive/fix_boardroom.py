with open('frontend/components/CommandCenter.tsx', 'r') as f:
    content = f.read()

# Add fetching of /energy/history
content = content.replace(
'''  const [state, setState] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      const stateRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/factory/state`)
      if (stateRes.ok) setState(await stateRes.json())
    }''',
'''  const [state, setState] = useState<any>(null)
  const [historyData, setHistoryData] = useState<any>(null)

  useEffect(() => {
    const fetchData = async () => {
      const stateRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/factory/state`)
      if (stateRes.ok) setState(await stateRes.json())
      const histRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'}/energy/history`)
      if (histRes.ok) setHistoryData(await histRes.json())
    }'''
)

with open('frontend/components/CommandCenter.tsx', 'w') as f:
    f.write(content)
