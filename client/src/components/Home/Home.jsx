import React from 'react'

export default class Home extends React.Component {

  render() {
    return (
      <span>
        <h3>Hello !</h3>
        <p className="welcome">Welcome to {this.props.config.name ? this.props.config.name: "Ludobox"} :)</p>
        <p>What would you like to do ?</p>
        <ul>
          <li>
            <a href="/games">Browse games on this box</a>
          </li>
          <li>
            <a href="/create">Create a new game</a>
          </li>
          <li>
            <a href="/download">Download games on my box</a>
          </li>
          <li>
            <a href="/about">Learn more about the Ludobox project</a>
          </li>
        </ul>
      </span>
    )
  }
}
