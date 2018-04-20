import { Result, HttpManagerService } from '../http-manager/http-manager.service';
import { MainService } from '../main/main.service';
import { Main } from '../main/main';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';
import { Observable } from 'rxjs/Observable';
import { of } from 'rxjs/observable/of';
import { find, findIndex } from 'lodash';
import { FdsScenario, FdsScenarioObject } from './fds-scenario';
import { Fds } from '../fds-object/fds-object';
import { Project } from '../project/project';
import { NotifierService } from 'angular-notifier';

@Injectable()
export class FdsScenarioService {

  main: Main;

  constructor(private mainService: MainService, private httpManager: HttpManagerService, private readonly notifierService: NotifierService) {
    this.mainService.getMain().subscribe(main => this.main = main);
  }

  /**
   * Set fds scenario to current
   * @param projectId 
   * @param fdsScenarioId 
   */
  setCurrentFdsScenario(projectId: number, fdsScenarioId: number): Observable<FdsScenario> {
    // Set current scenario in main object
    this.httpManager.get('https://aamks.inf.sgsp.edu.pl/api/fdsScenario/' + fdsScenarioId).then((result: Result) => {

      this.main.currentFdsScenario = new FdsScenario(JSON.stringify(result.data));
      this.main.currentRiskScenario = undefined;
      console.log(this.main.currentFdsScenario.fdsObject);

      // Set current project in main object
      let project = find(this.main.projects, function (o) {
        return o.id == projectId;
      });
      this.main.currentProject = project;

      this.notifierService.notify(result.meta.status, result.meta.details[0]);
    });

    return of(this.main.currentFdsScenario)
  }

  /** Create FDS scenario */
  createFdsScenario(projectId: number) {
    // Request
    this.httpManager.post('https://aamks.inf.sgsp.edu.pl/api/fdsScenario/' + projectId, JSON.stringify({})).then((result: Result) => {
      let data = result.data;
      let fdsScenario = new FdsScenario(JSON.stringify({ id: data['id'], projectId: data['projectId'], name: data['name'], fdsObject: new Fds(JSON.stringify({})) }));
      // add ui state in fdsscenario constructor ???
      this.main.currentProject.fdsScenarios.push(fdsScenario);
      this.notifierService.notify(result.meta.status, result.meta.details[0]);
    });
  }

  /**
   * Update FDS Scenario
   * @param projectId 
   * @param fdsScenarioId 
   * @param syncType Default value: 'all'
   */
  updateFdsScenario(projectId: number, fdsScenarioId: number, syncType: string = 'all') {

    // Sync only main info without fds object
    if (syncType == 'head') {
      let projectIndex = findIndex(this.main.projects, function (o) {
        return o.id == projectId;
      });
      let fdsScenarioIndex = findIndex(this.main.projects[projectIndex].fdsScenarios, function (o) {
        return o.id == fdsScenarioId;
      });
      let fdsScenario = this.main.projects[projectIndex].fdsScenarios[fdsScenarioIndex];
      this.httpManager.put('https://aamks.inf.sgsp.edu.pl/api/fdsScenario/' + fdsScenario.id, JSON.stringify({ type: "head", data: { id: fdsScenario.id, name: fdsScenario.name } })).then((result: Result) => {
        if (this.main.currentFdsScenario != undefined)
          this.main.currentFdsScenario = fdsScenario;

        this.notifierService.notify(result.meta.status, result.meta.details[0]);
      });
    }
    else if (syncType == 'all') {
      let fdsScenario = this.main.currentFdsScenario;
      this.httpManager.put('https://aamks.inf.sgsp.edu.pl/api/fdsScenario/' + fdsScenario.id, JSON.stringify({ type: 'all', data: fdsScenario.toJSON() })).then((result: Result) => {
        let projectIndex = findIndex(this.main.projects, function (o) {
          return o.id == projectId;
        });
        let fdsScenarioIndex = findIndex(this.main.projects[projectIndex].fdsScenarios, function (o) {
          return o.id == fdsScenarioId;
        });
        this.main.projects[projectIndex].fdsScenarios[fdsScenarioIndex] = fdsScenario;
        this.notifierService.notify(result.meta.status, result.meta.details[0]);
      });
    }
  }
  /** Delete FDS scenario */
  public deleteFdsScenario(projectIndex: number, fdsScenarioIndex: number) {
    let fdsScenarioId = this.main.projects[projectIndex].fdsScenarios[fdsScenarioIndex].id;
    this.httpManager.delete('https://aamks.inf.sgsp.edu.pl/api/fdsScenario/' + fdsScenarioId).then((result: Result) => {
      this.main.projects[projectIndex].fdsScenarios.splice(fdsScenarioIndex, 1);
      this.notifierService.notify(result.meta.status, result.meta.details[0]);
    });

  }

}
