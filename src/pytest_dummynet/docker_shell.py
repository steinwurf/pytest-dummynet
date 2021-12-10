import asyncio


class DockerShell(object):
    """A shell object for running commands"""

    def __init__(self, client, log, image_id):
        self.log = log
        self.container = client.containers.run(
            image=image_id,
            stdin_open=True,
            tty=True,
            auto_remove=True,
            command="/bin/sh",
            detach=True,
            network_mode="none",
            privileged=True,
        )

    def run(self, cmd: str, cwd=None, **kwargs):
        """Run a command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """
        self.log.debug(cmd)
        exit_code, output = self.container.exec_run(cmd, workdir=cwd, **kwargs)
        if exit_code != 0:
            raise RuntimeError(f"{cmd} failed with exit code {exit_code}\n{output}")
        else:
            if kwargs.get("demux", False):
                stdout, stderr = output
                return stdout.decode(), stderr.decode()
            return output.decode()

    async def run_async(self, cmd: str, daemon=False, delay=0, cwd=None):
        """Run an asynchronous command.
        :param cmd: The command to run
        :param cwd: The current working directory i.e. where the command will
            run
        """

        if delay > 0:
            self.log.debug(f"Waiting {delay} seconds")
            await asyncio.sleep(delay)

        self.log.debug("Running " + cmd)

        async def run_cmd():
            return self.container.exec_run(cmd, workdir=cwd, demux=True)

        task = asyncio.create_task(run_cmd())
        task.cmd = cmd
        task.daemon = daemon

        self.log.debug("Launched")

        try:
            exit_code, stdout, stderr = await task
        except asyncio.exceptions.CancelledError:
            if daemon:
                self.log.debug("Deamon shutting down")
            else:
                raise

        else:

            self.log.debug(f"[{cmd!r} exited with {exit_code}]")
            if stdout:
                self.log.info(f"[stdout]\n{stdout}")
            if stderr:
                self.log.info(f"[stderr]\n{stderr}")

            if daemon:
                raise RuntimeError("Deamon exit prematurely")

            if exit_code != 0:
                raise RuntimeError(f"{cmd} failed with exit code {exit_code}")

    def __del__(self):
        """Stop the container"""
        self.container.stop(timeout=1)
