# Official SysML v2 pilot implementation (OMG Systems Modeling), as a Jupyter kernel.
# I use it to validate the .sysml models and render their diagrams, without installing Java on my Mac.
FROM condaforge/miniforge3:24.11.3-2
ARG SYSML_VERSION=0.63.1
RUN conda install -y -c conda-forge "jupyter-sysml-kernel=${SYSML_VERSION}" "graphviz=2.*" jupyter_client \
    && conda clean -afy
WORKDIR /ws
