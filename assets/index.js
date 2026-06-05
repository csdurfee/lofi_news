function component() {
  const element = document.createElement('div');
  element.innerHTML = 'Hello HMR2Vite';
  return element;
}

document.body.appendChild(component());