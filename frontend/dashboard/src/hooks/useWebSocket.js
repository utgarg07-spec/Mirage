import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = 'ws://localhost:8000/ws'
const API_BASE = 'http://localhost:8000'

export default function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const [sessions, setSessions] = useState([])
  const [activeSessionId, setActiveSessionId] = useState(null)
  const [liveCommands, setLiveCommands] = useState({})
  const [predictions, setPredictions] = useState({})
  const [blockchainFeed, setBlockchainFeed] = useState([])
  const [networkAlert, setNetworkAlert] = useState(null)
  const [threatCount, setThreatCount] = useState(0)
  const wsRef = useRef(null)
  const reconnectTimer = useRef(null)

  const handleMessage = useCallback((msg) => {
    const { type, data } = msg

    if (type === 'initial_state') {
      if (data.sessions) setSessions(data.sessions)
    }
    else if (type === 'session_started') {
      setSessions(prev => [{
        session_id: data.session_id,
        ip_address: data.ip,
        username_tried: data.username,
        start_time: data.timestamp,
        is_active: 1,
        commands_count: 0
      }, ...prev])
    }
    else if (type === 'command_captured') {
      const { session_id, command, response, stage, confidence, 
              next_stage, skill_level, technique_tags } = data
      
      setLiveCommands(prev => ({
        ...prev,
        [session_id]: [...(prev[session_id] || []), {
          command, response, stage,
          timestamp: new Date().toISOString()
        }]
      }))
      
      setPredictions(prev => ({
        ...prev,
        [session_id]: {
          current_stage: stage,
          next_stage: next_stage || 'unknown',
          confidence: confidence || 0,
          skill_level: skill_level || 1,
          technique_tags: technique_tags || []
        }
      }))

      setSessions(prev => prev.map(s =>
        s.session_id === session_id
          ? { ...s, current_stage: stage, skill_level, is_active: 1 }
          : s
      ))
    }
    else if (type === 'session_ended') {
      setSessions(prev => prev.map(s =>
        s.session_id === data.session_id ? { ...s, is_active: 0 } : s
      ))
    }
    else if (type === 'threat_registered') {
      setBlockchainFeed(prev => [data, ...prev].slice(0, 20))
      setThreatCount(prev => prev + 1)
    }
    else if (type === 'network_alert') {
      setNetworkAlert(data)
      setTimeout(() => setNetworkAlert(null), 6000)
    }
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return

    console.log('[WS] Connecting to', WS_URL)
    const ws = new WebSocket('ws://localhost:8000/ws')
    wsRef.current = ws

    ws.onopen = () => {
      console.log('[WS] Connected')
      setIsConnected(true)
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current)
        reconnectTimer.current = null
      }
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        // Respond to server pings
        if (msg.type === 'ping') {
          ws.send(JSON.stringify({type: 'pong'}))
          return
        }
        console.log('[WS] Message:', msg.type, msg.data)
        handleMessage(msg)
      } catch (e) {
        console.error('[WS] Parse error:', e)
      }
    }

    ws.onerror = (err) => {
      console.error('[WS] Error:', err)
    }

    ws.onclose = (e) => {
      console.log('[WS] Closed, code:', e.code)
      setIsConnected(false)
      wsRef.current = null
      reconnectTimer.current = setTimeout(() => connect(), 3000)
    }

    // Send heartbeat every 20 seconds
    const heartbeat = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({type: 'ping'}))
      } else {
        clearInterval(heartbeat)
      }
    }, 20000)
  }, [handleMessage])

  useEffect(() => {
    connect()
    return () => {
      if (wsRef.current) wsRef.current.close()
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current)
    }
  }, [connect])

  // Poll threat count every 10 seconds as fallback
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const r = await fetch(`${API_BASE}/blockchain/threats/count`)
        const d = await r.json()
        setThreatCount(d.count || 0)
      } catch {
        /* ignore */
      }
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  return {
    isConnected, sessions, activeSessionId, setActiveSessionId,
    liveCommands, predictions, blockchainFeed, networkAlert,
    threatCount, setThreatCount
  }
}

