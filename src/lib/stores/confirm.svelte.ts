export interface ConfirmRequest {
  title: string
  message?: string
  confirmLabel?: string
  cancelLabel?: string
}

export interface OpenConfirm extends Required<ConfirmRequest> {
  id: number
}

export class ConfirmStore {
  current = $state<OpenConfirm | null>(null)
  private settle: ((answer: boolean) => void) | null = null
  private nextId = 1

  ask(request: ConfirmRequest): Promise<boolean> {
    this.answer(false)
    this.current = {
      id: this.nextId++,
      title: request.title,
      message: request.message ?? '',
      confirmLabel: request.confirmLabel ?? 'Yes',
      cancelLabel: request.cancelLabel ?? 'Keep it',
    }
    return new Promise((resolve) => {
      this.settle = resolve
    })
  }

  answer(value: boolean): void {
    const settle = this.settle
    this.settle = null
    this.current = null
    settle?.(value)
  }
}

export const confirmation = new ConfirmStore()
