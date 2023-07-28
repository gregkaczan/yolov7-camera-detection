module.exports = {
  apps: [
    {
      name: "detection-orchestrator",
      script: "python3",
      interpreter: "/usr/bin/env",
      args: "orchestrator.py",
      autorestart: true,
      watch: false,
    },
  ],
};