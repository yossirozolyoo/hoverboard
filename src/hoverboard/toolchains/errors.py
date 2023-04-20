class ToolchainError(Exception):
    pass


class ToolchainInstallationError(ToolchainError):
    pass


class ToolchainDecompressionFailed(ToolchainInstallationError):
    pass
